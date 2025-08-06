from construct import Byte, Int32ub, Struct, Int24ub, Bytes,BitStruct, BitsInteger
from features.security import encrypt_join_accept_payload, generate_join_accept_mic
from processing.device_registry import get_app_key, update_device_yaml_with_join_parameters, get_network_ids, store_devaddr_to_deveui_mapping
from join_accept_handling.Intialize_join_request_param import *

#Join accept structure
#PHYPayload = MHDR | Encrypted(MACPayload) | MIC
JoinAccept =Struct(
        AppNonce=Int24ub,
        NetID=Byte[3],
        DevAddr=Byte[4],
        DLSettings=Byte,
        RxDelay=Byte,
        CFList=Byte[16],  # Optional, But since we use EU 868 so we need to use it 
    )


# Define MHDR structure
MHDRStruct = BitStruct(
    "MType" / BitsInteger(3),  # Message Type: 0x01 for Join-Accept
    "RFU" / BitsInteger(3),    # Reserved for Future Use (set to 0)
    "Major" / BitsInteger(2)   # Major version: always 0 for LoRaWAN 1.0.x
)


def generate_join_accept_mhdr() -> bytes:
    mhdr_bits = MHDRStruct.build(dict(
        MType=0x01,  # Join-Accept
        RFU=0,
        Major=0      # LoRaWAN R1
    ))
    return mhdr_bits  # single byte

def intailize_join_request_parameters(dev_eui):
    """
    Initializes the Join Request frame structure
    Generates AppNonce
    assigns Devaddr  {NwkID -- NwkAddr }
    DLsettings (Downlink Settings) {RFU -- RX1DRoffset -- RX2 DataRate}
    RxDelay
    CF list  (list of channel frequencies)
    """
    nwk_id,nwk_addr=get_network_ids(dev_eui)

    return {
        "AppNonce": generate_app_nonce(),  # Int
        "NetID": nwk_id.to_bytes(3, "little"),  # 3 bytes
        "DevAddr": generate_device_addr(nwk_id, nwk_addr),  # 4 bytes
        "DLSettings": generate_dl_settings(),
        "RxDelay": generate_rx_delay(),
        "CFList": generate_cf_list()
    }

def generate_join_accept_payload(dev_eui):
    """
    Builds and returns a Join-Accept payload in bytes,
    and updates the DevAddr ↔ DevEUI mapping.
    """
    # Step 1: Initialize keys and values (AppNonce, DevAddr, etc.)
    payload_param = intailize_join_request_parameters(dev_eui)

    # Step 2: Update device YAML with keys
    update_device_yaml_with_join_parameters(dev_eui, payload_param)

    # Step 3: ⬇️ Extract DevAddr as hex string
    dev_addr_bytes = payload_param["DevAddr"]  # This is a bytes object (or list of ints)
    if isinstance(dev_addr_bytes, list):
        dev_addr_bytes = bytes(dev_addr_bytes)
    dev_addr_hex = dev_addr_bytes.hex().upper()

    # Step 4: Store mapping DevAddr → DevEUI
    store_devaddr_to_deveui_mapping(dev_addr_hex, dev_eui)

    # Step 5: Build Join-Accept payload (as per LoRaWAN)
    join_accept_payload = JoinAccept.build({
        "AppNonce": payload_param["AppNonce"],
        "NetID": list(payload_param["NetID"]),
        "DevAddr": list(payload_param["DevAddr"]),
        "DLSettings": payload_param["DLSettings"],
        "RxDelay": payload_param["RxDelay"],
        "CFList": list(payload_param["CFList"])
    })

    print(join_accept_payload)

    return join_accept_payload

 
def generate_join_accept_fullframe(dev_eui):
    # Step 1: Build raw MACPayload (unencrypted)
    join_accept_payload = generate_join_accept_payload(dev_eui)

    #Get the app_key that corresponds to teh dev_eui from the yaml file
    app_key=get_app_key(dev_eui)

    # Step 2: Build MHDR (MType = 0x01 for Join-Accept)
    mhdr = generate_join_accept_mhdr()

    print("JoinAccept Payload Length:", len(join_accept_payload))

    # Step 3: Encrypt MACPayload (with reversal, AES-ECB, and reverse again)
    encrypted_payload = encrypt_join_accept_payload(join_accept_payload, app_key)

    # Step 4: Compute MIC over MHDR + encrypted payload
    mic = generate_join_accept_mic(app_key, mhdr, encrypted_payload)

    # Step 5: Concatenate all parts: MHDR | EncryptedPayload | MIC
    full_packet = mhdr + encrypted_payload + mic

    return full_packet

def send_join_accept(dev_eui):
    """
    this fucntion is supposed to call a function to sedn teh data to teh end device
    """
    full_packet = generate_join_accept_fullframe(dev_eui)
    # TODO: send `full_packet` over your socket/radio/downlink queue
    #Need to send it somehow to an end device
    return full_packet
    
    
