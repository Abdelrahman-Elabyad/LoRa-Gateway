from tests.Tesing_main import handle_lorawan_packet
from config.settings import NWK_SKEY, APP_SKEY, SAMPLE_PACKET_BYTES
from features.mac_commands.mac_cmd_extraction import extract_mac_commands
from processing.update_device_yaml import update_device_yaml
from features.mac_commands.mac_cmd_handler import handle_mac_command_by_cid

def main():

    print("Packet length:", len(SAMPLE_PACKET_BYTES))
    print("Packet hex:", SAMPLE_PACKET_BYTES.hex().upper())

    # Optionally simulate decrypted MAC commands (if FPort = 0)
    frm_payload_decrypted = "7E500AB646"
    dev_addr = "01020304"  # Placeholder — update based on actual DevAddr if needed
    mac_commands = extract_mac_commands(bytes.fromhex(frm_payload_decrypted))
    parsed_outputs = [handle_mac_command_by_cid(cmd, i, 0) for i, cmd in enumerate(mac_commands)]
    update_device_yaml(parsed_outputs, dev_addr)
    print("Extracted MAC commands:", parsed_outputs)

    # Run your full parser handler
    handle_lorawan_packet(SAMPLE_PACKET_BYTES)

if __name__ == "__main__":
    main()
