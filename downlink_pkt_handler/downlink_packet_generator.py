import struct
from construct import Struct, Byte, Int8ul, Int16ul, Int32ul, GreedyBytes, BitStruct, BitsInteger, Bytes, this
from features.security import generate_mic, encrypt_payload
from features.NewSKey_AppSKey_generation import get_session_keys
from uplink_packet_handling.processing.device_registry import get_dev_addr_from_dev_eui, get_and_increment_fcnt_downlink
from uplink_packet_handling.processing.device_registry import get_device_session_keys

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
    # Build FHDR
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

#TODO: need to know how do i get the values for rfu and major
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

#TODO:need to make a fucnitn that makes the mac_cmd_downlink based on the mac cmds to be sent:either schedualed or responses

def downlink_pkt_build(mtype,mac_cmd_downlink,dev_eui,dev_addr):
    
    # Retrieve session keys 
    nwk_skey, app_skey = get_device_session_keys(dev_eui)
    
    # Get and increment the downlink frame counter
    #TODO: need to create the get_and_increment_fcnt_downlink function
    fcnt_down = get_and_increment_fcnt_downlink(dev_eui)

    # Build FOpts from MAC command responses
    fopts_bytes = b''.join(mac_cmd_downlink) if mac_cmd_downlink else b''

    # TODO: CALL THE FCtrl dictionary FUCNTION HERE TO GET THE VALUES BASED ON THE MAC CMDS
    fctrl_dict = create_fctrl_dict_based_on_mac_cmds(mac_cmd_downlink)
    # Example FRMPayload (empty for MAC commands only)
    frmpayload = b''

    # Build MACPayload
    mac_payload = mac_payload_builder(dev_addr, fctrl_dict, fcnt_down, fopts_bytes, fport=0 if frmpayload == b'' else 1, frmpayload=frmpayload)

    # Build MHDR
    mhdr = mhdr_builder(mtype)

    # Combine MHDR and MACPayload to form the PHY payload
    phy_payload = mhdr + mac_payload

    # Calculate MIC
    mic = generate_mic(nwk_skey, phy_payload, dev_addr, fcnt_down, direction=1)  # direction=1 for downlink

    # Final PHY payload with MIC
    final_phy_payload = phy_payload + mic

    return final_phy_payload