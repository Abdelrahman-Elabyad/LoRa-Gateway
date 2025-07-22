from protocol_layers.phy_layer import parse_phy_layer
from protocol_layers.mac_layer import parse_mac_layer
from protocol_layers.application_layer import parse_app_layer
from features.security import Physical_Layer_CRC_Checker
def parse_full_lorawan_frame(Packet_Data: bytes):
    """
    Parses a LoRaWAN packet into physical, MAC, and application layers.
    Also flattens key fields for direct use.
    """
    # --- Physical Layer ---
    physical_result = parse_phy_layer(Packet_Data)
    phy_payload = physical_result["PHYPayload"]

    phdr = bytes([physical_result["PHDR"]])
    phdr_crc = physical_result["PHDR_CRC"]  
    payload_crc = physical_result["PayloadCRC"]

    # --- MAC Layer ---
    #if not Physical_Layer_CRC_Checker(phdr, phdr_crc, phy_payload, payload_crc):
    #    raise ValueError("Invalid CRC in physical layer data")
    #else:
    mac_result = parse_mac_layer(phy_payload)
    mac_payload = mac_result["MACPayload"]

    # --- Application Layer ---
    #if not mac_payload:
    #    raise ValueError("MAC payload is empty or invalid")
    print("MACPayload hex:", mac_payload.hex().upper())
    app_result = parse_app_layer(mac_payload)

    # --- Extract & flatten fields ---
    fhdr = app_result["FHDR"]
    fctrl = fhdr["FCtrl"]
    mic_bytes = mac_result["MIC"]
    dev_addr_bytes = fhdr["DevAddr"]

    # Return everything
    return {
        "Preamble": physical_result["Preamble"],
        "PHDR": physical_result["PHDR"],
        "PHDR_CRC": physical_result["PHDR_CRC"],
        "PHY_Payload": physical_result["PHYPayload"],
        "MHDR": mac_result["MHDR"],
        "MIC": int.from_bytes(mic_bytes, "little") if isinstance(mic_bytes, (bytes, bytearray)) else mic_bytes,
        "DevAddr": int.from_bytes(dev_addr_bytes, "little") if isinstance(dev_addr_bytes, (bytes, bytearray)) else dev_addr_bytes,
        "FCtrl": fctrl,
        "FCnt": fhdr["FCnt"],
        "FOpts": fhdr["FOpts"],
        "FPort": app_result["FPort"],
        "FRMPayload": app_result["FRMPayload"],
        "ADR": fctrl["ADR"],
        "ADRACKReq": fctrl["ADRACKReq"],
        "ACK": fctrl["ACK"],
        "ClassB": fctrl["ClassB"],
        "FOptsLen": fctrl["FOptsLen"],

    }
