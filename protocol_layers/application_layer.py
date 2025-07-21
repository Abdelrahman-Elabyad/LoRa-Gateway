from construct import Struct, BitStruct, BitsInteger, Bytes, Int16ul, Byte, GreedyBytes, this

# FCtrl (Frame Control) contains MAC-level flags and FOpts length
FCtrl = BitStruct(
    "ADR" / BitsInteger(1),         # Adaptive Data Rate enabled
    "ADRACKReq" / BitsInteger(1),   # ADR acknowledgment request
    "ACK" / BitsInteger(1),         # Acknowledgment of confirmed frames
    "ClassB" / BitsInteger(1),      # Class B support indication
    "FOptsLen" / BitsInteger(4)     # Length of optional MAC commands in FOpts (0–15 bytes)
)

# Full LoRaWAN Application Frame (inside the MACPayload)
LoRaWANAPPFrame = Struct(
    "FHDR" / Struct(  # Frame Header
        "DevAddr" / Bytes(4),           # Device address (little endian)
        "FCtrl" / FCtrl,                # Frame control flags and FOpts length
        "FCnt" / Int16ul,               # Frame counter (2 bytes, uplink/downlink tracking)
        "FOpts" / Bytes(this.FCtrl.FOptsLen)  # Optional MAC commands (0–15 bytes)
    ),
    "FPort" / Byte,                     # Application port (1–223), 0 reserved for MAC-only
    "FRMPayload" / GreedyBytes         # Application payload (encrypted or MAC commands)
)
def parse_app_layer (MACPayload):
    