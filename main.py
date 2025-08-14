from packet_handling.uplink_packet_entry_point import handle_uplink_packet
import yaml
import os

def main():
    # Load the Join Request packet from YAML config
    yaml_path = "config/network_server_device_config.Yaml"
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"❌ YAML config not found at: {yaml_path}")

    with open(yaml_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Grab the first sample packet (assumed to be a Join Request)
    packet_hex = config["sample_packets"][0]["hex"]
    packet_bytes = bytes.fromhex(packet_hex)

    print("✅ Using Join Request packet from YAML")
    print("Packet length:", len(packet_bytes))
    print("Packet hex:", packet_bytes.hex().upper())

    # Only one required call:

    handle_uplink_packet(packet_bytes)

if __name__ == "__main__":
    main()
