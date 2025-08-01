from protocol_layers.mac_layer import parse_mac_layer
from protocol_layers.application_layer import parse_app_layer
from features.security import Physical_Layer_CRC_Checker, compute_verify_mic
from config.settings import NWK_SKEY, APP_SKEY
from parsing.mtype_utils import parse_lorawan_packet_by_type

def parse_full_lorawan_frame(phy_payload: bytes):
    """
    Parses a LoRaWAN packet into MAC, and application layers.
    Also flattens key fields for direct use.
    """

    # --- Mac Layer ---
    mac_result = parse_mac_layer(phy_payload)
    mac_payload = mac_result["MACPayload"]

    #Building MHDR byte from parsed MHDR fields
    mhdr_dict = mac_result["MHDR"]
    MHDR_byte = bytes([
        (mhdr_dict["MType"] & 0x07) |
        ((mhdr_dict["RFU"] & 0x07) << 3) |
        ((mhdr_dict["Major"] & 0x03) << 6)
    ])

    # --- Application Layer ---
    
    print("MACPayload hex:", mac_payload.hex().upper())
    app_result = parse_app_layer(mac_payload)

    # Check MIC
    if not compute_verify_mic(NWK_SKEY, app_result["FHDR"]["DevAddr"], app_result["FHDR"]["FCnt"], 0, MHDR_byte, mac_payload, mac_result["MIC"]):
        raise ValueError("Invalid MIC in MAC layer data")
    else:
        # --- Extract & flatten fields ---
        mic_bytes = mac_result["MIC"]

        # Return everything
        return {
            "MHDR": mac_result["MHDR"],
            "MType": mhdr_dict["MType"],
            "RFU": mhdr_dict["RFU"],
            "Major": mhdr_dict["Major"],
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
