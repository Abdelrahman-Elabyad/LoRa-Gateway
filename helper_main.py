from frame_parser import parse_full_lorawan_frame
from processing.mac_cmd_processing import process_mac_commands
from processing.write_device_yaml import generate_device_yaml
from config.settings import SAMPLE_PACKET_BYTES

def handle_lorawan_packet(packet_data: bytes):
    # Step 1: Parse the full LoRaWAN frame
    parsed_packet = parse_full_lorawan_frame(packet_data)
    # Print parsed results
    for key, value in parsed_packet.items():
            print(f"{key}: {value}")
    # Step 2: Extract MType
    mtype = parsed_packet["MType"]
    dev_addr= parsed_packet["DevAddr"]
    mac_cmmands={}
    # Step 3: Switch on MType and handle accordingly
    match mtype:
        case 0:
            # Join Request
            print("Join Request (MType=0): No MAC command processing needed.")
            #Nedd to add other fucntions here so that it does what the mmessage type corresponds to 
        case 1:
            # Join Accept
            print("Join Accept (MType=1): No MAC command processing needed.")

        case 2:
            # Unconfirmed Data Up
            #No ack needed
            print("Unconfirmed Data Up (MType=2): Processing MAC commands...")
            mac_cmmands = process_mac_commands(parsed_packet)
            print(mac_cmmands)

        case 3:
            # Unconfirmed Data Down
            #No ack needed
            print("Unconfirmed Data Down (MType=3): Processing MAC commands...")
            mac_cmmands = process_mac_commands(parsed_packet)
            print(mac_cmmands)

        case 4:
            # Confirmed Data Up
            #ack needed
            print("Confirmed Data Up (MType=4): Processing MAC commands...")
            mac_cmmands = process_mac_commands(parsed_packet)
            print(mac_cmmands)

        case 5:
            # Confirmed Data Down
            #ack needed
            print("Confirmed Data Down (MType=5): Processing MAC commands...")
            mac_cmmands = process_mac_commands(parsed_packet)
            print(mac_cmmands)

        case 6:
            # RFU (Reserved for Future Use)
            print("RFU (MType=6): Skipping MAC processing.")

        case 7:
            # Proprietary Frame
            print("Proprietary Frame (MType=7): Skipping MAC processing.")

        case _:
            # Unknown MType
            print(f"Unknown MType ({mtype}): Unable to determine processing action.")

    if mac_cmmands != {}:
        generate_device_yaml(mac_cmmands,dev_addr)
        
