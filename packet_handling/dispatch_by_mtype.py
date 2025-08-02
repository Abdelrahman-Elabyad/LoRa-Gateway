from packet_handling.join_request_parser import parse_join_request
from packet_handling.data_uplink_handler import handle_data_uplink()
from processing.device_registry import genrate_update_device_yaml_file
from processing.mac_cmd_processing import process_mac_commands

def parse_lorawan_packet_by_type(mtype: int, Packet_data: bytes,mhdr, mhdr_byte: dict, mac_payload: bytes, mic: bytes):
    
    if mtype == 0:
        parsed_frame=parse_join_request(Packet_data)
        dev_eui = parsed_frame["DevEUI"]
        app_eui = parsed_frame["AppEUI"]
        dev_nonce = parsed_frame["DevNonce"]
        mac_cmd_dict= {}
        genrate_update_device_yaml_file(mac_cmd_dict,dev_eui, app_eui, dev_nonce, output_dir="device_config")
        send_join_accept()

    elif mtype in [2, 4]:
        parsed_frame=handle_data_uplink(mtype, mhdr, mhdr_byte, mic, mac_payload)
        mac_cmd_dict=process_mac_commands(parsed_frame)
        dev_eui = parsed_frame["DevEUI"]
        app_eui = parsed_frame["AppEUI"]
        dev_nonce = parsed_frame["DevNonce"]
        genrate_update_device_yaml_file(mac_cmd_dict,dev_eui, app_eui, dev_nonce, output_dir="device_config")
        #confirmed_data_up_packet need to send an acknowledgment
        if mtype ==4 :
            send_acknowledgment(parsed_frame) #fucntion used to send the acknowledgment in RX1 or RX2 window

    else:
        raise ValueError(f"Unsupported or unexpected MType for uplink: {mtype}")

