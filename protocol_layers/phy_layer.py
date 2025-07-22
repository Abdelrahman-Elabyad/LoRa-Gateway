# Construct is used as its much and compatibale with the raspberry pi better than any library on python
# file: phy/full_phy_parser.py
from construct import Struct, Byte, Bytes, GreedyBytes

LoRaPhysicalFrame = Struct(
    "Preamble" / Bytes(8),             # Usually fixed to 0x55 * 8 or similar
    "PHDR" / Byte,                     # Physical Header
    "PHDR_CRC" / Byte,                 # Header CRC
    "PHYPayloadAndCRC" / GreedyBytes   # All remaining bytes (payload + CRC)
)

def parse_phy_layer(lora_data: bytes):
    parsed = LoRaPhysicalFrame.parse(lora_data)
    payload_and_crc = parsed.PHYPayloadAndCRC
    if len(payload_and_crc) >= 2:
        phy_payload = payload_and_crc[:-2]
        payload_crc = int.from_bytes(payload_and_crc[-2:], "little")
    else:
        phy_payload = payload_and_crc
        payload_crc = None
    return {
        "Preamble": parsed.Preamble,
        "PHDR": parsed.PHDR,
        "PHDR_CRC": parsed.PHDR_CRC,
        "PHYPayload": phy_payload,
        "PayloadCRC": payload_crc
    }
