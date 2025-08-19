from join_request_parser import parse_join_request
from data_uplink_handler import handle_data_uplink
from uplink_packet_handling.uplink_mac_cmd_handler.mac_cmd_processing import process_mac_commands
from downlink_pkt_handler.join_accept_handling.join_accept_generator import generate_join_accept_fullframe
from features.NewSKey_AppSKey_generation import generate_session_keys
from processing.device_registry import initialize_device_yaml,update_device_yaml_with_session_keys, update_device_yaml_settings_from_mac_cmds, get_dev_eui_from_dev_addr,update_network_server_yaml_file,add_metadata_to_device_yaml, get_meta_data_from_device_yaml
from downlink_pkt_handler.downlink_mac_cmd_builder.mac_cmd_responses import analyse_mac_cmds
from features.acknowedgment import send_acknowledgment
from NS_shim.time_stamp     import fetch_pkt_timestamp, compute_rx_timestamps
from NS_shim.downlink_json_obj_generator import downlink_wrap_pkt_into_json
def parse_lorawan_packet_by_type(mtype: int, Packet_data: bytes,mhdr, mhdr_byte: dict, mac_payload: bytes, mic: bytes, meta_data: dict):
    
    if mtype == 0:
        parsed_frame=parse_join_request(Packet_data)
        dev_eui = parsed_frame["DevEUI"]
        app_eui = parsed_frame["AppEUI"]
        dev_nonce = parsed_frame["DevNonce"]
        initialize_device_yaml(dev_eui, app_eui, dev_nonce)
        add_metadata_to_device_yaml(meta_data)
        join_accept_packet=generate_join_accept_fullframe(dev_eui)
        nwk_skey,app_skey=generate_session_keys(dev_eui)
        update_device_yaml_with_session_keys(dev_eui, nwk_skey, app_skey)
        tmst,freq,rfch,powe,modu,datr,codr,ipol,rx1_tmst,rx2_tmst=get_meta_data_from_device_yaml(meta_data)
        dl_tmst=decide_recive_window()
        downlink_json= downlink_wrap_pkt_into_json (join_accept_packet,dl_tmst,freq,rfch,powe,modu,datr,codr,ipol)
        #result_summary  = {"Type": "JoinRequest", "DevEUI": dev_eui}

    elif mtype in [2, 4]:
        parsed_frame=handle_data_uplink(mtype, mhdr, mhdr_byte, mic, mac_payload)
        dev_addr=parsed_frame["DevAddr"]
        dev_eui= get_dev_eui_from_dev_addr(dev_addr)
        mac_cmd_dict=process_mac_commands(parsed_frame,dev_eui)
        settings_dict=analyse_mac_cmds(mac_cmd_dict)
        ####
        tmst=fetch_pkt_timestamp()
        update_network_server_yaml_file(tmst)
        rx1_tmst,rx2_tmst=compute_rx_timestamps()
        update_device_yaml_file_with_meta_data(dev_eui,rx1_tmst, rx2_tmst)
        ####
        update_device_yaml_settings_from_mac_cmds(dev_eui, settings_dict)
        #confirmed_data_up_packet need to send an acknowledgment

        ###### TODO: need to adjsut thsi for teh json builder and the output packet
        if mtype ==4 :
            #need to give it the values needed to construct the ack msg
            send_acknowledgment(settings_dict) #fucntion used to send the acknowledgment in RX1 or RX2 window

    else:
        raise ValueError(f"Unsupported or unexpected MType for uplink: {mtype}")

