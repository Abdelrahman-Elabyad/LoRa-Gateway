from parsing.join_request_parser import parse_join_request
from parsing.data_up_parser import parse_data_up_packet


def parse_lorawan_packet_by_type(mtype: int, Packet_data: bytes,mhdr, mhdr_byte: dict, mac_payload: bytes, mic: bytes):
    
    if mtype == 0:
        return parse_join_request(Packet_data)

    elif mtype in [2, 4]:
        return parse_data_up_packet(mtype, mhdr, mhdr_byte, mic, mac_payload)

    else:
        raise ValueError(f"Unsupported or unexpected MType for uplink: {mtype}")

