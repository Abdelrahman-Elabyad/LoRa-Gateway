from construct import Struct, BitStruct, BitsInteger, Bytes, GreedyBytes
from features.security import Physical_Layer_CRC_Checker

LoRaWANMacFrame = Struct(
        "MHDR" / BitStruct(
            "MType" / BitsInteger(3),
            "RFU" / BitsInteger(3),
            "Major" / BitsInteger(2)
        ),
        "MACPayloadAndMIC" / GreedyBytes

)
def parse_mac_layer(phy_payload: bytes):

    # Parse MAC
    parsed_mac = LoRaWANMacFrame.parse(phy_payload)
    payload_and_mic = parsed_mac.MACPayloadAndMIC
    mac_payload = payload_and_mic[:-4] if len(payload_and_mic) >= 4 else payload_and_mic
    mic = payload_and_mic[-4:] if len(payload_and_mic) >= 4 else b""

    return {
        "MHDR": {
            "MType": parsed_mac.MHDR.MType,
            "RFU": parsed_mac.MHDR.RFU,
            "Major": parsed_mac.MHDR.Major
        },
        "MACPayload": mac_payload,
        "MIC": mic
    }
