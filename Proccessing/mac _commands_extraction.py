#MAC commands 
from frame_parser import parse_full_lorawan_frame
from features.mac_commands import extract_mac_commands handle_mac_command_by_cid
from features.security import decrypt_frm_payload
from config.settings import NWK_SKEY, APP_SKEY

def mac_commands_fetch(packet_data: bytes):
    """
    Parses a LoRaWAN packet and extracts MAC commands.
    """
    try:
        parsed_frame = parse_full_lorawan_frame(packet_data)
        
        # Extract needed fields from parsed layers
        fopts       = parsed_frame["application_layer"]["FHDR"]["FOpts"]
        fopts_len   = parsed_frame["application_layer"]["FHDR"]["FCtrl"]["FOptsLen"]
        fport       = parsed_frame["application_layer"]["FPort"]
        frmpayload  = parsed_frame["application_layer"]["FRMPayload"]
        dev_addr    = parsed_frame["application_layer"]["FHDR"]["DevAddr"]
        fcnt        = parsed_frame["application_layer"]["FHDR"]["FCnt"]
        mtype       = parsed_frame["mac_layer"]["MHDR"]["MType"] #This is to be used if i wanted to make this a 

    #Mac commands are Piggybacked in the FOpts field
        if fopts_len > 0 and fport!=0:
            mac_commands = extract_mac_commands(fopts)
            return mac_commands
    #Mac commands are in the Frmpayload after decryption    
        elif len(frmpayload) > 0 and fport==0:
            decrypted_frmpayload = decrypt_frm_payload(
                app_skey=APP_SKEY,
                nwkskey=NWK_SKEY,
                dev_addr=dev_addr,
                fcnt=fcnt,
                direction=0,  # Assuming uplink
                frm_payload=frmpayload,
                Fport=fport
            )
            mac_commands = extract_mac_commands(decrypted_frmpayload)
            parsed_outputs = [handle_mac_command_by_cid(cmd, i) for i, cmd in enumerate(mac_commands)]
            return {"source": "FRMPayload", "commands": mac_commands}

        return {"message": "No MAC commands found in FOpts or FRMPayload."}
    
    except ValueError as e:
        return {"error": str(e)}
