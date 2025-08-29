from functools import reduce
from operator import xor
import numpy as np
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.cmac import CMAC
from cryptography.hazmat.primitives.ciphers import algorithms

#You calculate AES-CMAC over B0 + msg(MHDR | MACPayload)
#Then take the first 4 bytes as your MIC
def generate_mic(nwkskey: bytes, devaddr: bytes, fcnt: int, direction: int, MHDR: bytes, MacPayload: bytes) -> bytes:
    #Intialiaze CMAC with AES algorithm
    cmac = CMAC(algorithms.AES(nwkskey))

    #Since the FCnt is stored using little endain convention we need to shift it
    fcnt_bytes = fcnt_to_little_endian_bytes(fcnt, 2)  # 2 is the number of bytes dedicated to the FCnt
    devaddr_bytes = devaddr.to_bytes(4, 'little')

    # Build B0 block (16 bytes total)
    B0 = bytes([
        0x49,                         # Fixed value for LoRaWAN MIC
        0x00, 0x00, 0x00, 0x00,       # Reserved
        direction & 0x01,             # 0 = uplink, 1 = downlink
        *devaddr_bytes,               # DevAddr (little-endian)
        *fcnt_bytes,                  # FCnt (padded to 4 bytes little-endian)
        0x00,                         # Reserved (always 0)
        len(MHDR) + len(MacPayload)   # Total length of MHDR + MACPayload
    ])

    cmac.update(B0 + MHDR + MacPayload)
    return cmac.finalize()[:4]

def compute_verify_mic(nwkskey: bytes, devaddr: bytes, fcnt: int, direction: int, MHDR: bytes, MacPayload: bytes, MIC) -> bool:
    mic_generated = generate_mic(nwkskey, devaddr, fcnt, direction, MHDR, MacPayload)
    MIC_HEX = MIC.hex().upper() if isinstance(MIC, bytes) else MIC
    print("MIC from packet:", MIC_HEX)
    calculated_mic = mic_generated.hex().upper()
    print("Calculated MIC:", calculated_mic)
    return calculated_mic == MIC_HEX


#MIC for Join Request is calculated using a different method
#It uses the APP_KEY and Join Request payload to calculate the MIC
#NO B0 Block is used here
#The Join Request payload is the MHDR + MACPayload (18 bytes total)
def compute_join_request_mic(app_key: bytes, join__request_payload: bytes) -> bytes:
    """
    Computes the MIC for a Join Request message as per LoRaWAN 1.0.3 spec.
    
    :param app_key: 16-byte AppKey (bytes)
    :param join_payload: MHDR + MACPayload (18 bytes total)
    :return: 4-byte MIC
    """
    cmac = CMAC(algorithms.AES(app_key))
    cmac.update(join__request_payload)  # No B0 prefix in Join Request MIC
    return cmac.finalize()[:4]


#Helper Function for the FCnt conversion 
def fcnt_to_little_endian_bytes(fcnt: int, Bytes: int) -> bytes:
    """
    Converts a FCnt integer to little-endian bytes.
    Since FCnt was stored as an integer then we need to use little endain agin while formatting it
    """
    if Bytes == 2:
        return fcnt.to_bytes(2, 'little') + b'\x00\x00'  # Pad to 4 bytes
    elif Bytes == 4:
        return fcnt.to_bytes(4, 'little')
    else:
        raise ValueError("FCnt must be 16 or 32 bits")

#NO CBC *Cipher Block CHnainig is done 
#We formulate the J block in teh CTR encryption mode as per LoRaWAN specification (section 4.3.3)
#First we encrypt the A block (which is the J block) using ECB mode (each block on its own )
#Then the result is XORed with the FRMPayload (Padded if needed) to get the decrypted payload
#Decrypted[i] = FRMPayload[i] XOR S_block[i]
def decrypt_frm_payload(app_skey: bytes,nwkskey:bytes, dev_addr: bytes, fcnt: int, direction: int, frm_payload: bytes, Fport: int) -> bytes:
    """
    Decrypts the FRMPayload using AES-CTR mode as per LoRaWAN specification (section 4.3.3),
    with vectorized XOR via NumPy for better performance.

    Args:
        app_skey (bytes): 16-byte session key (AppSKey or NwkSKey).
        dev_addr (bytes): 4-byte device address (little endian).
        fcnt (int): 2-byte frame counter.
        direction (int): 0 = uplink, 1 = downlink.
        frm_payload (bytes): Encrypted payload.

    Returns:
        bytes: Decrypted payload.
    """
    if (len(app_skey) and len(nwkskey))!= 16:
        raise ValueError("Both AppSKey and NwkSKey must be 16 bytes")
     # Select the correct key based on FPort
    if Fport == 0:
        key = nwkskey
    else:
        key = app_skey

    aes_cipher = AES.new(key, AES.MODE_ECB)
    payload_len = len(frm_payload)
    num_blocks = (payload_len + 15) // 16
    decrypted = bytearray()

    for i in range(num_blocks):
        # --- Construct A block (encryption block for AES CTR) ---
        a_block = bytearray(16)
        a_block[0] = 0x01
        a_block[5] = direction & 0x01
        a_block[6:10] = dev_addr.to_bytes(4, 'little')
        a_block[10:12] = fcnt.to_bytes(2, 'little')
        a_block[15] = (i + 1) & 0xFF  # Counter starts at 1

        # --- Encrypt A block to get S block ---
        s_block = aes_cipher.encrypt(bytes(a_block))

        # --- Slice current 16-byte chunk from payload ---
        start = i * 16
        end = min(start + 16, payload_len)
        frm_chunk = frm_payload[start:end]

        # --- XOR using NumPy (vectorized) ---
        frm_arr = np.frombuffer(frm_chunk, dtype=np.uint8)
        s_arr = np.frombuffer(s_block, dtype=np.uint8)[:len(frm_chunk)]

        decrypted_chunk = np.bitwise_xor(frm_arr, s_arr).tobytes()
        decrypted.extend(decrypted_chunk)

    return bytes(decrypted)

# This function is used to encrypt FRMPayload messages
def encrypt_frm_payload(app_skey: bytes, nwkskey: bytes, dev_addr: bytes, fcnt: int, direction: int, frm_payload: bytes, Fport: int) -> bytes:
    return decrypt_frm_payload(
        app_skey=app_skey,
        nwkskey=nwkskey,
        dev_addr=dev_addr,
        fcnt=fcnt,
        direction=1,     # Assuming downlink for encryption
        frm_payload=frm_payload,
        Fport=Fport
    )


def encrypt_join_accept_payload(mac_payload: bytes, app_key: bytes) -> bytes:
    """
    Encrypts the Join-Accept payload using LoRaWAN 1.0.x spec:
    Reverse → Pad to 16-byte block → AES-128 ECB encrypt → Reverse again

    Args:
        mac_payload: Raw Join-Accept MACPayload (AppNonce to CFList, typically 28 bytes)
        app_key: 16-byte AppKey used for AES encryption

    Returns:
        Encrypted Join-Accept payload as bytes (reversed back and trimmed to original length)
    """
    # Step 1: Reverse the plaintext
    reversed_payload = mac_payload[::-1]

    # Step 2: Pad to 16-byte block
    pad_len = (16 - len(reversed_payload) % 16) % 16
    padded = reversed_payload + b"\x00" * pad_len

    # Step 3: Encrypt using AES-ECB
    cipher = Cipher(algorithms.AES(app_key), modes.ECB())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(padded) + encryptor.finalize()

    # Step 4: Reverse encrypted result and trim to original length
    encrypted_payload = encrypted[::-1][:len(mac_payload)]

    return encrypted_payload


def generate_join_accept_mic(app_key: bytes, mhdr: bytes, join_accept_payload: bytes) -> bytes:
    """
    Computes the MIC for the Join-Accept message using AES-CMAC (LoRaWAN 1.0.x spec).

    Args:
        app_key: 16-byte AppKey
        mhdr: 1-byte MHDR (should be 0x20 for Join-Accept)
        join_accept_payload: encrypted Join-Accept payload (after AES-ECB encryption)

    Returns:
        4-byte MIC as bytes
    """
    if not isinstance(mhdr, bytes):
        mhdr = bytes([mhdr])  # Convert int to 1-byte

    message = mhdr + join_accept_payload

    cmac = CMAC(algorithms.AES(app_key))
    cmac.update(message)
    return cmac.finalize()[:4]



