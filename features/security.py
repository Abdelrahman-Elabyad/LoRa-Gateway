import binascii
from functools import reduce
from operator import xor
from cryptography.hazmat.primitives.cmac import CMAC
from cryptography.hazmat.primitives.ciphers import algorithms

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

