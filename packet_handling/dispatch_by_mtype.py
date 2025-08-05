from packet_handling.join_request_parser import parse_join_request
from packet_handling.data_uplink_handler import handle_data_uplink
from processing.mac_cmd_processing import process_mac_commands
from join_accept_handling.join_accept_generator import send_join_accept
from processing.device_registry import genrate_update_device_yaml_file  
from Key_generation.NewSKey_AppSKey_generation import generate_session_keys
from processing.device_registry import update_device_yaml_with_session_keys, initialize_device_yaml, update_device_yaml_settings_from_mac_cmds
def parse_lorawan_packet_by_type(mtype: int, Packet_data: bytes,mhdr, mhdr_byte: dict, mac_payload: bytes, mic: bytes):
    
    if mtype == 0:
        parsed_frame=parse_join_request(Packet_data)
        dev_eui = parsed_frame["DevEUI"]
        app_eui = parsed_frame["AppEUI"]
        dev_nonce = parsed_frame["DevNonce"]
        mac_cmd_dict= None
        initialize_device_yaml(dev_eui, app_eui, dev_nonce, output_dir="device_config")
        app_nonce, dev_addr, net_id=send_join_accept()
        #from it get the NewSKey and AppSKey
        nwk_skey,app_skey=generate_session_keys(dev_eui: str, app_nonce: bytes, net_id: bytes, dev_nonce: bytes,config_path)
        update_device_yaml_with_session_keys(dev_eui, app_nonce, dev_addr, net_id, nwk_skey, app_skey, output_dir="device_config")

    elif mtype in [2, 4]:
        parsed_frame=handle_data_uplink(mtype, mhdr, mhdr_byte, mic, mac_payload)
        mac_cmd_dict=process_mac_commands(parsed_frame)
        dev_eui = parsed_frame["DevEUI"]
        app_eui = parsed_frame["AppEUI"]
        dev_nonce = parsed_frame["DevNonce"]
        analyse_mac_cmds()
        update_device_yaml_settings_from_mac_cmds(dev_eui, settings_dict, output_dir="device_config")
        #confirmed_data_up_packet need to send an acknowledgment
        if mtype ==4 :
            send_acknowledgment(parsed_frame) #fucntion used to send the acknowledgment in RX1 or RX2 window

    else:
        raise ValueError(f"Unsupported or unexpected MType for uplink: {mtype}")

