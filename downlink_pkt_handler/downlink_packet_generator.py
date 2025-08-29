import struct
from construct import Struct, Byte, Int8ul, Int16ul, Int32ul, GreedyBytes, BitStruct, BitsInteger, Bytes, this
from features.security import calculate_mic, encrypt_payload

#the fctrl_dict is a dictionary with the keys ADR, ADRACKReq, ACK, ClassB
#TODO:need to add a fucntin that genrates the fctrl dict based on the mac cmds to be sent
def fhdr_builder(dev_addr, fctrl_dict, fcnt, fopts_bytes):
    # Define the FCtrl structure
    FCtrl = BitStruct(
        "ADR" / BitsInteger(1),         # Adaptive Data Rate enabled
        "ADRACKReq" / BitsInteger(1),   # ADR acknowledgment request
        "ACK" / BitsInteger(1),         # Acknowledgment of confirmed frames
        "ClassB" / BitsInteger(1),      # Class B support indication
        "FOptsLen" / BitsInteger(4)     # Length of optional MAC commands in FOpts (0–15 bytes)
    )

    # Build the FCtrl field
    fctrl = FCtrl.build({
        "ADR": fctrl_dict.get("ADR", 0),
        "ADRACKReq": fctrl_dict.get("ADRACKReq", 0),
        "ACK": fctrl_dict.get("ACK", 0),
        "ClassB": fctrl_dict.get("ClassB", 0),
        "FOptsLen": len(fopts_bytes)
    })

    # Define the FHDR structure
    FHDR = Struct(
        "DevAddr" / Int32ul,  # Device address (little endian)
        "FCtrl" / FCtrl,                # Frame control flags and FOpts length
        "FCnt" / Int16ul,               # Frame counter (2 bytes, uplink/downlink tracking)
        "FOpts" / Bytes(len(fopts_bytes))  # Optional MAC commands (0–15 bytes) Variable length
    )

    # Build the FHDR
    fhdr = FHDR.build({
        "DevAddr": dev_addr,
        "FCtrl": {
            "ADR": fctrl_dict.get("ADR", 0),
            "ADRACKReq": fctrl_dict.get("ADRACKReq", 0),
            "ACK": fctrl_dict.get("ACK", 0),
            "ClassB": fctrl_dict.get("ClassB", 0),
            "FOptsLen": len(fopts_bytes)
        },
        "FCnt": fcnt,
        "FOpts": fopts_bytes
    })

    return fhdr
def mac_payload_builder(dev_addr,fctrl_dict,fcnt,fopts_bytes,fport,frmpayload):
    fhdr=fhdr_builder(dev_addr, fctrl_dict, fcnt, fopts_bytes)
    # Define the MACPayload structure
    LoRaWANMACPayload = Struct(
        "FHDR" / fhdr,
        "FPort" / Byte,
        "FRMPayload" / GreedyBytes
    )
    
    # Build the MACPayload
    mac_payload = LoRaWANMACPayload.build({
        "FHDR": fhdr,
        "FPort": fport,
        "FRMPayload": frmpayload
    })

    return mac_payload 
def mhdr_builder(mtype, rfu=0, major=0):
    # Define the MHDR structure
    MHDR = BitStruct(
        "MType" / BitsInteger(3),
        "RFU" / BitsInteger(3),
        "Major" / BitsInteger(2)
    )

    # Build the MHDR
    mhdr = MHDR.build({
        "MType": mtype,
        "RFU": rfu,
        "Major": major
    })

    return mhdr





def downlink_pkt_build(mtype,mac_cmd_responses,dev_eui):
