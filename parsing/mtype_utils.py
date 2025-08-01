from parsing.frame_parser import parse_full_lorawan_frame
from parsing.join_request_parser import parse_join_request

#This fucntion should be used to help make descisions on how to interpret a packet recieved
def parse_lorawan_packet_by_type(mtype: int, data: bytes):
    """
    Dispatcher to parse LoRaWAN packet based on MType
    """
    match mtype:
        case 0:  # Join Request
            return parse_join_request(data)
        case 2 | 4:  # Unconfirmed/Confirmed Data Up
            return parse_full_lorawan_frame(data)
        case _:  # Not expected
            raise ValueError(f"Unsupported or unexpected MType for uplink: {mtype}")

