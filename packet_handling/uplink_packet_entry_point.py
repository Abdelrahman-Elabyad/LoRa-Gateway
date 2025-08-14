from protocol_layers.mac_layer import parse_mac_layer
from packet_handling.dispatch_by_mtype import parse_lorawan_packet_by_type  
from NS_shim.uplink_gw_pkt__handler import lora_packet_extractor

def handle_uplink_packet(push_data_json):
    """
    Entry point: Parses any LoRaWAN uplink packet and returns a flat, structured dictionary.
    Handles JoinRequest and DataUp types via MType-specific routing.
    """
    #extract the data from the json object outputted from the concentrator
    lorawan_packet_hex=lora_packet_extractor(push_data_json)
    
    #start the parsing of the lorawan packet 
    mac_result = parse_mac_layer(lorawan_packet_hex)

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
    return parse_lorawan_packet_by_type( mtype, lorawan_packet_hex, mhdr, mhdr_byte, mic, mac_payload)

    