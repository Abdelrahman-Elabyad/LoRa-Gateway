from Parsing.frame_parser import parse_full_lorawan_frame

def main():
    # Example raw packet (hex string converted to bytes)
    sample_packet_hex = "AAAAAAAAAAAAAAAA40404001020304040100AABBCCDD03DEADBEEF000000004620"

    packet_bytes = bytes.fromhex(sample_packet_hex)
    print("Packet length:", len(packet_bytes))
    print("Packet hex:", packet_bytes.hex().upper())

    parsed = parse_full_lorawan_frame(packet_bytes)
    # Print parsed results
    for key, value in parsed.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    main()