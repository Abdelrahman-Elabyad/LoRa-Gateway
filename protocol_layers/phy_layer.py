# Construct is used as its much and compatibale with the raspberry pi better than any library on python
# file: phy/full_phy_parser.py
from construct import Struct, Byte, Bytes, Int16ul, GreedyBytes,GreedyRange

LoRaPhysicalFrame = Struct(
    "Preamble" / Bytes(8),             # Usually fixed to 0x55 * 8 or similar
    "PHDR" / Byte,                     # Physical Header
    "PHDR_CRC" / Byte,                 # Header CRC
    "PHYPayload" / GreedyRange(Byte)[:-2],  # All remaining bytes except last 2   # Stores all the bytes between the PHDR_CRC and the the last 2 bytes of the Payload_CRC
    "PayloadCRC" / Int16ul             # CRC of payload (Stored using Little Endian convention the LSB are on the left)
)

#Function that uses the Packet and passes it on the pysical layer parser to return the physical payload
def parse_phy_layer(lora_data: bytes):
    parsed = LoRaPhysicalFrame.parse(lora_data)
    # Return raw LoRaWAN PHYPayload for next layer (MAC Layer)
    return {
        "preamble": parsed.Preamble,
        "PHDR": parsed.PHDR,
        "PHDR_CRC": parsed.PHDR_CRC,
        "PHYPayload": parsed.PHYPayload,
        "PayloadCRC": parsed.PayloadCRC
    }
