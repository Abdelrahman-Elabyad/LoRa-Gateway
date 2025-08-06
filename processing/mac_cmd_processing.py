#MAC commands 
from features.mac_commands.mac_cmd_extraction import extract_mac_commands
from features.mac_commands.mac_cmd_handler import handle_uplink_mac_command_by_cid
from features.security import decrypt_frm_payload
from processing.device_registry import get_device_session_keys

def process_mac_commands(parsed_frame,dev_eui):
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

    #Mac commands are Piggybacked in the FOpts field
        if fopts_len > 0 and fport!=0:
            mac_commands = extract_mac_commands(fopts)
            decoded_mac_commands = [handle_uplink_mac_command_by_cid(cmd, i, direction) for i, cmd in enumerate(mac_commands)]
            return decoded_mac_commands
    #Mac commands are in the Frmpayload after decryption    
        elif len(frmpayload) > 0 and fport==0:
            app_skey,nwk_skey=get_device_session_keys(dev_eui)
            decrypted_frmpayload = decrypt_frm_payload(app_skey, nwk_skey, dev_addr, fcnt, direction, frmpayload, fport)
            mac_commands = extract_mac_commands(decrypted_frmpayload)
            decoded_mac_commands = [handle_uplink_mac_command_by_cid(cmd, i,direction) for i, cmd in enumerate(mac_commands)]
            return decoded_mac_commands

        return {"message": "No MAC commands found in FOpts or FRMPayload."}

    except ValueError as e:
        return {"error": str(e)}
