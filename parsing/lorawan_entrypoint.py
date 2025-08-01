from protocol_layers.mac_layer import parse_mac_layer
from parsing.mtype_utils import parse_lorawan_packet_by_type

def process_lorawan_packet(phy_payload):
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
    MType = mhdr_dict["MType"]

    parse_lorawan_packet_by_type(MType, phy_payload)
