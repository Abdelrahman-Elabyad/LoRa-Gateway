import binascii
from functools import reduce
from operator import xor
import numpy as np
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.cmac import CMAC
from cryptography.hazmat.primitives.ciphers import algorithms
from Crypto.Cipher import AES



# --- Payload CRC: 16-bit CRC using standard polynomial 
def verify_crc(payload_bytes: bytes, received_crc: int) -> bool:
    """
    Verifies a standard 2-byte CRC for PHY Payload using CRC-16 (X.25)
    """
    return binascii.crc_hqx(payload_bytes, 0x0000) == received_crc

# --- PHDR CRC: 1-byte XOR-based checksum (LoRa-style)
def verify_phdr_crc(phdr_bytes: bytes, received_crc: int) -> bool:
    """
    Verifies 1-byte XOR checksum for PHDR field
    """
    computed_crc = reduce(xor, phdr_bytes, 0x00)
    return computed_crc == received_crc

# --- Combined Physical Layer CRC Check
def Physical_Layer_CRC_Checker(phdr: bytes, phdr_crc: int, phy_payload: bytes, payload_crc: int) -> bool:
    """
    Verifies both PHDR_CRC (1 byte) and Payload CRC (2 bytes)
    """
    return verify_phdr_crc(phdr, phdr_crc) and verify_crc(phy_payload, payload_crc)


#You calculate AES-CMAC over B0 + msg(MHDR | MACPayload)
#Then take the first 4 bytes as your MIC
def compute_verify_mic(nwkskey: bytes, devaddr: bytes, fcnt: int, direction: int, MHDR: bytes, MacPayload: bytes,MIC) -> bytes:
    """
    Computes the 4-byte MIC for a LoRaWAN message.
    :param nwkskey: 16-byte network session key (bytes)
    :param devaddr: 4-byte DevAddr in little-endian (bytes)
    :param fcnt: 2-byte or 4-byte FCnt (int)
    :param direction: 0 for uplink, 1 for downlink
    :param payload: Full MHDR + MACPayload (bytes)
    """
    #Intialiaze CMAC with AES algorithm
    cmac = CMAC(algorithms.AES(nwkskey))

    #Since the FCnt is stored using little endain convention we need to shift it
    fcnt_bytes = fcnt_to_little_endian_bytes(fcnt, 2)  # 2 is the number of bytes dedicated to the FCnt
    devaddr_bytes = devaddr.to_bytes(4, 'little')

    # Build B0 block (16 bytes total)
    B0 = bytes([
        0x49,                         # Fixed value for LoRaWAN MIC
        0x00, 0x00, 0x00, 0x00,       # Reserved
        direction & 0x01,            # 0 = uplink, 1 = downlink
        *devaddr_bytes,                    # DevAddr (little-endian)
        *fcnt_bytes,                 # FCnt (padded to 4 bytes little-endian)
        0x00,                        # Reserved (always 0)
        len(MHDR) + len(MacPayload)  # Total length of MHDR + MACPayload
    ])

    cmac.update(B0 + MHDR + MacPayload)
    calculated_cmac = cmac.finalize()  

    MIC_HEX = MIC.hex().upper() if isinstance(MIC, bytes) else MIC
    print("MIC from packet:", MIC_HEX)
    calculated_mic = calculated_cmac[:4].hex().upper()
    print("Calculated MIC:", calculated_mic)
    return calculated_mic == MIC_HEX



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
