import binascii
from functools import reduce
from operator import xor

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
