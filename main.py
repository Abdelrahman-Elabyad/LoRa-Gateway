from helper_main    import handle_lorawan_packet
from config.settings import SAMPLE_PACKET_BYTES, NWK_SKEY, APP_SKEY
from features.security import decrypt_frm_payload
from features.mac_commands.mac_cmd_extraction import extract_mac_commands
from processing.write_device_yaml import generate_device_yaml
from processing.mac_cmd_processing import process_mac_commands
from features.mac_commands.mac_cmd_handler import handle_mac_command_by_cid
def main():
    print("Packet length:", len(SAMPLE_PACKET_BYTES))
    print("Packet hex:", SAMPLE_PACKET_BYTES.hex().upper())
    frm_payload_decrepted="7E500AB646"
    dev_addr = "01020304"  # Example DevAddr, replace with actual value
    mac_commands = extract_mac_commands(bytes.fromhex(frm_payload_decrepted))
    parsed_outputs = [handle_mac_command_by_cid(cmd, i, 0) for i, cmd in enumerate(mac_commands)]
    generate_device_yaml(parsed_outputs, dev_addr)
    print("Extracted MAC commands:", parsed_outputs)
    handle_lorawan_packet(SAMPLE_PACKET_BYTES)

if __name__ == "__main__":
    main()