from Parsing.frame_parser import parse_full_lorawan_frame
from config.settings import SAMPLE_PACKET_BYTES, NWK_SKEY, APP_SKEY
def main():
    print("Packet length:", len(SAMPLE_PACKET_BYTES))
    print("Packet hex:", SAMPLE_PACKET_BYTES.hex().upper())

    parsed = parse_full_lorawan_frame(SAMPLE_PACKET_BYTES)
    # Print parsed results
    for key, value in parsed.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    main()