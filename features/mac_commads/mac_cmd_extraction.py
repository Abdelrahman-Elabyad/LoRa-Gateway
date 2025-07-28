# MAC command definitions: CID -> (Name, PayloadLength)
#This is a dictionary that maps the CID to the name of the MAC command and its payload length
# This has the MAC commands that are sent by bothe the end device and the Gateway

MAC_COMMANDS = {
    0x02: ("LinkCheckReq", 0),
    0x82: ("LinkCheckAns", 2),
    0x03: ("LinkADRReq", 4),
    0x83: ("LinkADRAns", 1),
    0x04: ("DutyCycleReq", 1),
    0x84: ("DutyCycleAns", 0),
    0x05: ("RXParamSetupReq", 4),
    0x85: ("RXParamSetupAns", 1),
    0x06: ("DevStatusReq", 0),
    0x86: ("DevStatusAns", 2),
    0x07: ("NewChannelReq", 5),
    0x87: ("NewChannelAns", 1),
    0x08: ("RXTimingSetupReq", 1),
    0x88: ("RXTimingSetupAns", 0),
    0x09: ("TxParamSetupReq", 1),
    0x89: ("TxParamSetupAns", 0),
    0x0A: ("DlChannelReq", 4),
    0x8A: ("DlChannelAns", 1),
    0x0B: ("RekeyInd", 1),
    0x8B: ("RekeyConf", 1),
    0x0C: ("ADRParamSetupReq", 1),
    0x8C: ("ADRParamSetupAns", 0),
    0x0D: ("DeviceTimeReq", 0),
    0x8D: ("DeviceTimeAns", 5),
    0x0E: ("ForceRejoinReq", 2),
    0x8E: ("RejoinParamSetupReq", 1),
    0x8F: ("RejoinParamSetupAns", 1),
}

#Not able to do Vectorization as this process is completly sequential
#This fucntion is only used to get the Mac Commands frm a given stream of bytes
#It is used to parse the mac commands from either the FRM payload after decryption or from the FOpts field

def extract_mac_commands(mac_bytes: bytes):

    i = 0
    commands = []
    append = commands.append  # local binding for speed

    while i < len(mac_bytes):
        cid = mac_bytes[i]
        i += 1
        name, length = MAC_COMMANDS.get(cid, (f"UnknownCID_{cid:02X}", 0))
        payload = mac_bytes[i:i+length] if length else b""
        append({
            "CID": f"0x{cid:02X}",
            "Name": name,
            "Payload": payload.hex().upper() if payload else None
        })
        i += length

    return commands
