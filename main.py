import json
import sys
import os
from uplink_packet_handling.uplink_packet_entry_point import handle_uplink_packet
#sample_packets:
#- description: OTAA Join Request (valid MIC, LSB format)
#  hex: 00887766554433221108070605040302011234F20B8567
#- description: Physical payload (MAC Layer only)
#  hex: 400403020100010148656C6C6FAABBCCDD

# Add the path to your module
sys.path.append(os.path.abspath("uplink_packet_handling"))

# Sample Join Request JSON (Semtech UDP format)
sample_json = {
    "rxpk": [
        {
            "time": "2025-08-14T10:20:30.123456Z",
            "tmst": 123456789,
            "chan": 2,
            "rfch": 0,
            "freq": 868.300000,
            "stat": 1,
            "modu": "LORA",
            "datr": "SF7BW125",
            "codr": "4/5",
            "lsnr": 7.5,
            "rssi": -45,
            "size": 23,
            "data": "AIh3ZlVEMyIRCAcGBQQDAgESNPILhWc="
        }
    ]
}

if __name__ == "__main__":
    handle_uplink_packet(sample_json)


