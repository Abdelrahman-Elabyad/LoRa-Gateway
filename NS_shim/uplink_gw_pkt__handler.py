import json
import base64
"""
This script loads a LoRaWAN uplink packet from a JSON file, extracts the Base64-encoded PHYPayload and timestamp,
decodes the payload to bytes, and prints the Base64 string, raw bytes, and hexadecimal representation.
Steps performed:
1. Loads a JSON file named "push_data.json" containing LoRaWAN packet data.
2. Extracts the Base64-encoded PHYPayload from the first 'rxpk' entry.
"""
def lora_packet_extractor():
    # Load JSON file
    with open("NS_shim/push_data.json", "r") as f:
        push_data = json.load(f)

    # Extract Base64 LoRaWAN packet
    lora_pkt_base64 = push_data["rxpk"][0]["data"]

    # Decode Base64 to bytes
    phy_bytes = base64.b64decode(lora_pkt_base64)
    lora_pkt_hex = phy_bytes.hex().upper()
    return lora_pkt_hex


