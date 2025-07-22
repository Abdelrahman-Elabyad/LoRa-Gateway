from construct import Struct, BitStruct, BitsInteger, Bytes, GreedyBytes

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
    mhdr = parsed_mac.MHDR
    payload_and_mic = parsed_mac.MACPayloadAndMIC
    mac_payload = payload_and_mic[:-4] if len(payload_and_mic) >= 4 else payload_and_mic
    mic = payload_and_mic[-4:]
    print("MACPayloadAndMIC:", payload_and_mic.hex().upper())
    print("MACPayload len:", len(payload_and_mic))

    return {
        "MHDR": {
            "MType": mhdr.MType,
            "RFU": mhdr.RFU,
            "Major": mhdr.Major
        },
        "MACPayload": mac_payload,
        "MIC": mic
    }
