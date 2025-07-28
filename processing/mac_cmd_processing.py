#MAC commands 
from frame_parser import parse_full_lorawan_frame
from features.mac_commands.mac_cmd_extraction import extract_mac_commands
from features.mac_commands.mac_cmd_handler import handle_mac_command_by_cid
from features.security import decrypt_frm_payload
from config.settings import NWK_SKEY, APP_SKEY

def process_mac_commands(parsed_frame):
    """
    Parses a LoRaWAN packet and extracts MAC commands.
    """
    try:
        direction=0  # Assuming uplink direction for MAC commands extraction

        # Extract needed fields from parsed layers
        fopts       = parsed_frame["FOpts"]
        fopts_len   = parsed_frame["FOptsLen"]
        fport       = parsed_frame["FPort"]
        frmpayload  = parsed_frame["FRMPayload"]
        dev_addr    = parsed_frame["DevAddr"]
        fcnt        = parsed_frame["FCnt"]
        mtype       = parsed_frame["MType"] #check the notes file to know how to use this

    #Mac commands are Piggybacked in the FOpts field
        if fopts_len > 0 and fport!=0:
            mac_commands = extract_mac_commands(fopts)
            parsed_outputs = [handle_mac_command_by_cid(cmd, i, direction) for i, cmd in enumerate(mac_commands)]
            return parsed_outputs
    #Mac commands are in the Frmpayload after decryption    
        elif len(frmpayload) > 0 and fport==0:
            decrypted_frmpayload = decrypt_frm_payload(APP_SKEY, NWK_SKEY, dev_addr, fcnt, direction, frmpayload, fport)
            mac_commands = extract_mac_commands(decrypted_frmpayload)
            parsed_outputs = [handle_mac_command_by_cid(cmd, i,direction) for i, cmd in enumerate(mac_commands)]
            return parsed_outputs

        return {"message": "No MAC commands found in FOpts or FRMPayload."}

    except ValueError as e:
        return {"error": str(e)}
