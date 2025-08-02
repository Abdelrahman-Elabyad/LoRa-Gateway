
from construct import Struct, Bytes
#According to the lorawan Specification 1.0.3 
#the device already has DEVEUI and APPEUI and AppKey set up Before the Join request is sent 
    #DevEUI is a gloabl unique identifier for the device in IEEE EUI-64 format
    #AppEUI is a globally unique identifier for the application in IEEE EUI-64 format
    #AppKey is a 128-BIT AES encryption key used for securing the join procedure and subsequent communication
JoinRequestFrame = Struct(
        "MHDR" / Bytes(1),
        "MacPayload" / Struct(
            "AppEUI" / Bytes(8),
            "DevEUI" / Bytes(8),
            "DevNonce" / Bytes(2)
        ),
        "MIC" / Bytes(4)
    )

def parse_join_request(packet_data: bytes):
    """
    Parses a Join Request message and returns its fields in a flat structure.
    """
    parsed = JoinRequestFrame.parse(packet_data)

    return {
        "Type": "JoinRequest",
        "MHDR": parsed.MHDR.hex().upper(),
        "AppEUI": parsed.MacPayload.AppEUI.hex().upper(),
        "DevEUI": parsed.MacPayload.DevEUI.hex().upper(),
        "DevNonce": parsed.MacPayload.DevNonce.hex().upper(),
        "MIC": parsed.MIC.hex().upper()
    }

