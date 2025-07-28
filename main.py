from helper_main    import handle_lorawan_packet
from config.settings import SAMPLE_PACKET_BYTES, NWK_SKEY, APP_SKEY
from features.security import decrypt_frm_payload
from features.mac_commands.mac_cmd_extraction import extract_mac_commands
def main():
    print("Packet length:", len(SAMPLE_PACKET_BYTES))
    print("Packet hex:", SAMPLE_PACKET_BYTES.hex().upper())
    mac_commands="03AABBCCDD0419"

    output=extract_mac_commands(bytes.fromhex(mac_commands))
    print("Extracted MAC commands:", output)
    handle_lorawan_packet(SAMPLE_PACKET_BYTES)

if __name__ == "__main__":
    main()