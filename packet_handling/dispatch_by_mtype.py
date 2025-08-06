from packet_handling.join_request_parser import parse_join_request
from packet_handling.data_uplink_handler import handle_data_uplink
from processing.mac_cmd_processing import process_mac_commands
from join_accept_handling.join_accept_generator import send_join_accept
from Key_generation.NewSKey_AppSKey_generation import generate_session_keys
from processing.device_registry import initialize_device_yaml,update_device_yaml_with_session_keys, update_device_yaml_settings_from_mac_cmds, get_dev_eui_from_dev_addr
from features.mac_commands.mac_cmd_responses import analyse_mac_cmds
from features.acknowedgment import send_acknowledgment
def parse_lorawan_packet_by_type(mtype: int, Packet_data: bytes,mhdr, mhdr_byte: dict, mac_payload: bytes, mic: bytes):
    
    if mtype == 0:
        parsed_frame=parse_join_request(Packet_data)
        dev_eui = parsed_frame["DevEUI"]
        app_eui = parsed_frame["AppEUI"]
        dev_nonce = parsed_frame["DevNonce"]
        initialize_device_yaml(dev_eui, app_eui, dev_nonce)
        join_accept_packet=send_join_accept(dev_eui)
        nwk_skey,app_skey=generate_session_keys(dev_eui)
        update_device_yaml_with_session_keys(dev_eui, nwk_skey, app_skey)
        print(join_accept_packet)
    elif mtype in [2, 4]:
        parsed_frame=handle_data_uplink(mtype, mhdr, mhdr_byte, mic, mac_payload)
        dev_addr=parsed_frame["DevAddr"]
        dev_eui= get_dev_eui_from_dev_addr(dev_addr)
        mac_cmd_dict=process_mac_commands(parsed_frame,dev_eui)
        settings_dict=analyse_mac_cmds(mac_cmd_dict)
        update_device_yaml_settings_from_mac_cmds(dev_eui, settings_dict)
        #confirmed_data_up_packet need to send an acknowledgment
        if mtype ==4 :
            #need to give it the values needed to construct the ack msg
            send_acknowledgment(settings_dict) #fucntion used to send the acknowledgment in RX1 or RX2 window

    else:
        raise ValueError(f"Unsupported or unexpected MType for uplink: {mtype}")

