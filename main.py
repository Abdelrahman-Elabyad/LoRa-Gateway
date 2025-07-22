from Parsing.frame_parser import parse_full_lorawan_frame

def main():
    # Example raw packet (hex string converted to bytes)
    sample_packet_hex = "AAAAAAAAAAAAAAAA4001400102030400010203FF1122334455"
    packet_bytes = bytes.fromhex(sample_packet_hex)
    
    parsed = parse_full_lorawan_frame(packet_bytes)
    # Print parsed results
    for key, value in parsed.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    main()