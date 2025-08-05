from construct import Byte, Int32ub, Struct, Int24ub, Bytes,BitStruct, BitsInteger
from features.security import encrypt_join_accept_payload, generate_join_accept_mic

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

def intailize_join_request_parameters():
    """
    Initializes the Join Request frame structure
    Generates AppNonce
    assigns Devaddr  {NwkID -- NwkAddr }
    DLsettings (Downlink Settings) {RFU -- RX1DRoffset -- RX2 DataRate}
    RxDelay
    CF list  (list of channel frequencies)
    """
    nwk_id = 0x12
    nwk_addr = 0x34567

    return {
        "AppNonce": generate_app_nonce(),  # Int
        "NetID": nwk_id.to_bytes(3, "little"),  # 3 bytes
        "DevAddr": generate_device_addr(nwk_id, nwk_addr),  # 4 bytes
        "DLSettings": generate_dl_settings(),
        "RxDelay": generate_rx_delay(),
        "CFList": generate_cf_list()
    }

def generate_join_accept_payload():
    """
    Builds and returns a Join accept Payload in bytes.
    """
    # Get all required fields
    params = intailize_join_request_parameters()

    # Use construct to build the Join-Accept binary structure
    join_accept_payload = JoinAccept.build({
        "AppNonce": params["AppNonce"],
        "NetID": list(params["NetID"]),         # convert bytes to list of 3 integers
        ""
        "": list(params["DevAddr"]),     # convert bytes to list of 4 integers
        "DLSettings": params["DLSettings"],
        "RxDelay": params["RxDelay"],
        "CFList": list(params["CFList"])        # convert 16-byte array to list of ints
    })
    # Encrypt (reverse → AES-ECB → reverse)
    
    return join_accept_payload
 
def generate_join_accept_fullframe():
    # Step 1: Build raw MACPayload (unencrypted)
    join_accept_payload = generate_join_accept_payload()

    # Step 2: Build MHDR (MType = 0x01 for Join-Accept)
    mhdr = generate_join_accept_mhdr()

    # Step 3: Encrypt MACPayload (with reversal, AES-ECB, and reverse again)
    encrypted_payload = encrypt_join_accept_payload(join_accept_payload, app_key)

    # Step 4: Compute MIC over MHDR + encrypted payload
    mic = generate_join_accept_mic(app_key, mhdr, encrypted_payload)

    # Step 5: Concatenate all parts: MHDR | EncryptedPayload | MIC
    full_packet = mhdr + encrypted_payload + mic

    return full_packet

def send_join_accept():
    """
    this fucntion is supposed to call a function to sedn teh data to teh end device
    """
    
