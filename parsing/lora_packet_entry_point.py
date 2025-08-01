from protocol_layers.mac_layer import parse_mac_layer
from parsing.parse_packet_by_mtype import parse_lorawan_packet_by_type  


def parse_full_lorawan_frame(Packet_data: bytes):
    """
    Entry point: Parses any LoRaWAN uplink packet and returns a flat, structured dictionary.
    Handles JoinRequest and DataUp types via MType-specific routing.
    """
    mac_result = parse_mac_layer(Packet_data)

    # Extract fields from MAC result
    mtype = mac_result["MHDR"]["MType"]
    mhdr = mac_result["MHDR"]
    mac_payload = mac_result["MACPayload"]
    mic = mac_result["MIC"]

    # Rebuild MHDR byte for MIC calculation (inside downstream function)
    mhdr_byte = bytes([
        (mhdr["MType"] & 0x07) |
        ((mhdr["RFU"] & 0x07) << 3) |
        ((mhdr["Major"] & 0x03) << 6)
    ])

    # Delegate to MType-specific parser
    return parse_lorawan_packet_by_type( mtype, Packet_data, mhdr, mhdr_byte, mic, mac_payload)

    