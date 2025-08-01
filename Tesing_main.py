from parsing.lora_packet_entry_point import parse_full_lorawan_frame
from processing.mac_cmd_processing import process_mac_commands
from processing.update_device_yaml import update_device_yaml
from config.settings import SAMPLE_PACKET_BYTES

def handle_lorawan_packet(packet_data: bytes):
    """
    Main entry point for handling LoRaWAN packets.
    Parses the packet, processes MAC commands, and generates device YAML.
    """

    # Parse the full LoRaWAN frame
    parsed_frame = parse_full_lorawan_frame(packet_data)
    Message_Type = parsed_frame["Type"]

    if Message_Type == "ConfirmedDataUp" or Message_Type == "UnconfirmedDataUp":
        print("Processing Data Up packet")
        # Process MAC commands if present
        mac_commands_result = process_mac_commands(parsed_frame)
    elif Message_Type == "JoinRequest":
        # Generate device YAML from parsed frame
        print("Processing Join Request packet")
    print("Parsed Frame:", parsed_frame)
    print("MAC Commands Result:", mac_commands_result if 'mac_commands_result' in locals() else "No MAC commands processed")

        
