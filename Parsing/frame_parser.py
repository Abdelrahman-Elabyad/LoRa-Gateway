from protocol_layers.phy_layer import parse_phy_layer
from protocol_layers.mac_layer import parse_mac_layer
from protocol_layers.application_layer import parse_app_layer
from features.security import Physical_Layer_CRC_Checker, compute_verify_mic
from config.settings import NWK_SKEY, APP_SKEY
def parse_full_lorawan_frame(Packet_Data: bytes):
    """
    Parses a LoRaWAN packet into physical, MAC, and application layers.
    Also flattens key fields for direct use.
    """
    # --- Physical Layer ---
    physical_result = parse_phy_layer(Packet_Data)

    phdr = bytes([physical_result["PHDR"]]) if isinstance(physical_result["PHDR"], int) else physical_result["PHDR"]
    phdr_crc = physical_result["PHDR_CRC"]
    phy_payload = physical_result["PHYPayload"]
    payload_crc = physical_result["PayloadCRC"]


    # --- MAC Layer ---
    if not Physical_Layer_CRC_Checker(phdr, phdr_crc, phy_payload, payload_crc):
        raise ValueError("Invalid CRC in physical layer data")
    else:
        mac_result = parse_mac_layer(phy_payload)
        mac_payload = mac_result["MACPayload"]

    # --- Application Layer ---
    
    print("MACPayload hex:", mac_payload.hex().upper())
    app_result = parse_app_layer(mac_payload)
    #Building MHDR byte from parsed MHDR fields
    mhdr_dict = mac_result["MHDR"]
    MHDR_byte = bytes([
        (mhdr_dict["MType"] & 0x07) |
        ((mhdr_dict["RFU"] & 0x07) << 3) |
        ((mhdr_dict["Major"] & 0x03) << 6)
    ])

    if not compute_verify_mic(NWK_SKEY, app_result["FHDR"]["DevAddr"], app_result["FHDR"]["FCnt"], 0, MHDR_byte, mac_payload, mac_result["MIC"]):
        raise ValueError("Invalid MIC in MAC layer data")
    else:
        # --- Extract & flatten fields ---
        mic_bytes = mac_result["MIC"]

        # Return everything
        return {
            "Preamble": physical_result["Preamble"],
            "PHDR": physical_result["PHDR"],
            "PHDR_CRC": physical_result["PHDR_CRC"],
            "PHY_Payload": physical_result["PHYPayload"],
            "MHDR": mac_result["MHDR"],
            "MIC": int.from_bytes(mic_bytes, "little") if isinstance(mic_bytes, (bytes, bytearray)) else mic_bytes,
            "DevAddr": app_result["FHDR"]["DevAddr"],
            "FCtrl": app_result["FHDR"]["FCtrl"],
            "FCnt": int.from_bytes(app_result["FHDR"]["FCnt"], "little") if isinstance(app_result["FHDR"]["FCnt"], (bytes, bytearray)) else app_result["FHDR"]["FCnt"],
            "FOpts": app_result["FHDR"]["FOpts"],
            "FPort": app_result["FPort"],
            "FRMPayload": app_result["FRMPayload"],
            "ADR": app_result["FHDR"]["FCtrl"]["ADR"],
            "ADRACKReq": app_result["FHDR"]["FCtrl"]["ADRACKReq"],
            "ACK": app_result["FHDR"]["FCtrl"]["ACK"],
            "ClassB": app_result["FHDR"]["FCtrl"]["ClassB"],
            "FOptsLen": app_result["FHDR"]["FCtrl"]["FOptsLen"],

        }
