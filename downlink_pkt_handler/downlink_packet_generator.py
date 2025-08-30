import struct
from construct import BitStruct, BitsInteger
from features.security import generate_mic, encrypt_frm_payload
from uplink_packet_handling.processing.device_registry import get_and_increment_fcnt_downlink, get_device_session_keys
#Just to be able to add teh commit meassage for the downilink packet generation part 
#the fctrl_dict is a dictionary with the keys ADR, RFU, ACK, FPending
def fhdr_builder(dev_addr, fctrl_dict, fcnt, fopts_bytes):
    # Define the FCtrl structure (Downlink: ADR | RFU | ACK | FPending | FOptsLen)
    FCtrlDown = BitStruct(
        "ADR" / BitsInteger(1),        # Adaptive Data Rate enabled
        "RFU" / BitsInteger(1),        # Reserved for future use (must be 0)
        "ACK" / BitsInteger(1),        # Acknowledgment of confirmed uplink
        "FPending" / BitsInteger(1),   # Indicates more frames pending
        "FOptsLen" / BitsInteger(4)    # Length of MAC commands in FOpts (0–15 bytes)
    )

    if len(fopts_bytes) > 15:
        raise ValueError("FOpts exceeds 15 bytes; move MAC commands to FRMPayload with FPort=0.")

    # Normalize DevAddr to int (accepts int, bytes, or hex string)
    if isinstance(dev_addr, (bytes, bytearray)):
        if len(dev_addr) != 4:
            raise ValueError("DevAddr bytes must be 4 bytes (little-endian).")
        dev_addr_int = int.from_bytes(dev_addr, "little")
    elif isinstance(dev_addr, int):
        dev_addr_int = dev_addr
    else:
        dev_addr_int = int(str(dev_addr), 16)

    # Build the FCtrl field
    fctrl = FCtrlDown.build({
        "ADR": fctrl_dict.get("ADR", 0),
        "RFU": fctrl_dict.get("RFU", 0),      # keep 0
        "ACK": fctrl_dict.get("ACK", 0),
        "FPending": fctrl_dict.get("FPending", 0),
        "FOptsLen": len(fopts_bytes)
    })

    # DevAddr (Int32 LE), FCtrl (1B), FCnt (2B LE), FOpts (0–15B)
    fhdr = (
        dev_addr_int.to_bytes(4, "little") +     # DevAddr (little endian)
        fctrl +                                  # FCtrl
        (fcnt & 0xFFFF).to_bytes(2, "little") +  # Frame counter (2 bytes)
        fopts_bytes                              # Optional MAC commands
    )
    return fhdr, dev_addr_int  # return both FHDR and normalized DevAddr

def mac_payload_builder(dev_addr_int, fctrl_dict, fcnt, fopts_bytes, fport, frmpayload):
    # Build FHDR
    fhdr, _ = fhdr_builder(dev_addr_int, fctrl_dict, fcnt, fopts_bytes)
    # Only include FPort if FRMPayload is present
    if frmpayload and fport is not None:
        return fhdr + bytes([fport]) + frmpayload
    return fhdr  # no FRMPayload => omit FPort

#the major and rfu are always 0 for LoRaWAN 1.0.x
def mhdr_builder(mtype, rfu=0, major=0):
    MHDR = BitStruct(
        "MType" / BitsInteger(3),  # Message type
        "RFU" / BitsInteger(3),    # Reserved, must be 0
        "Major" / BitsInteger(2)   # LoRaWAN major version (0 for R1 = 1.0.x/1.1)
    )
    return MHDR.build({"MType": mtype, "RFU": rfu, "Major": major})

#It should be in the appropriate format (list of bytes)
def downlink_pkt_build(mtype, mac_cmd_downlink, dev_eui, dev_addr, application_data: bytes = b"", application_fport: int = 1):
    # Retrieve session keys 
    nwk_skey_hex, app_skey_hex = get_device_session_keys(dev_eui)
    nwk_skey = bytes.fromhex(nwk_skey_hex)
    app_skey = bytes.fromhex(app_skey_hex)

    # Get and increment the downlink frame counter
    fcnt_down = get_and_increment_fcnt_downlink(dev_eui)

    # Build FOpts from MAC command responses (≤ 15B). If larger, must move to FRMPayload@FPort=0
    mac_bytes = b"".join(mac_cmd_downlink) if mac_cmd_downlink else b""
    has_app_data = bool(application_data)

    if len(mac_bytes) <= 15:
        fopts_bytes = mac_bytes
        mac_cmds_in_frm = b""
        chosen_fport = None
    else:
        # Too large for FOpts. If app data also present → conflict
        if has_app_data:
            raise ValueError("MAC commands >15B cannot share FRMPayload with application data. Send in a separate downlink.")
        fopts_bytes = b""
        mac_cmds_in_frm = mac_bytes
        chosen_fport = 0  # FRMPayload will carry MAC commands (encrypted with NwkSKey)

    # TODO:Build the FCtrl dictionary (ACK/ADR/FPending) from MAC command logic
    fctrl_dict = create_fctrl_dict_based_on_mac_cmds(mac_cmd_downlink)
    fctrl_dict.setdefault("RFU", 0)

    # Normalize DevAddr once and reuse
    if isinstance(dev_addr, (bytes, bytearray)):
        dev_addr_int = int.from_bytes(dev_addr, "little")
    elif isinstance(dev_addr, int):
        dev_addr_int = dev_addr
    else:
        dev_addr_int = int(str(dev_addr), 16)

    # Build MACPayload
    if mac_cmds_in_frm:  # case: MAC commands >15B, no app data
        enc_frm = encrypt_frm_payload(app_skey, nwk_skey, dev_addr_int, fcnt_down, 1, mac_cmds_in_frm, Fport=0)
        mac_payload = mac_payload_builder(dev_addr_int, fctrl_dict, fcnt_down, fopts_bytes, fport=0, frmpayload=enc_frm)
    elif has_app_data:  # case: application data present
        if application_fport == 0:
            raise ValueError("application_fport=0 is reserved for MAC commands.")
        enc_app = encrypt_frm_payload(app_skey, nwk_skey, dev_addr_int, fcnt_down, 1, application_data, Fport=application_fport)
        mac_payload = mac_payload_builder(dev_addr_int, fctrl_dict, fcnt_down, fopts_bytes, fport=application_fport, frmpayload=enc_app)
    else:  # case: only FOpts or empty downlink
        mac_payload = mac_payload_builder(dev_addr_int, fctrl_dict, fcnt_down, fopts_bytes, fport=None, frmpayload=b"")

    # Build MHDR (LoRaWAN 1.0.x: RFU=0, Major=0). MType=3 for UnconfirmedDataDown, 5 for ConfirmedDataDown
    mhdr = mhdr_builder(mtype, rfu=0, major=0)

    # Calculate MIC over B0 | MHDR | MACPayload (direction=1 for downlink)
    mic = generate_mic(nwk_skey, dev_addr_int, fcnt_down, 1, mhdr, mac_payload)

    # Final PHYPayload = MHDR | MACPayload | MIC
    return mhdr + mac_payload + mic
