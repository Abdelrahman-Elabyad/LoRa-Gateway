from helper_main    import handle_lorawan_packet
from config.settings import SAMPLE_PACKET_BYTES, NWK_SKEY, APP_SKEY
def main():
    print("Packet length:", len(SAMPLE_PACKET_BYTES))
    print("Packet hex:", SAMPLE_PACKET_BYTES.hex().upper())

    handle_lorawan_packet(SAMPLE_PACKET_BYTES)
   

if __name__ == "__main__":
    main()