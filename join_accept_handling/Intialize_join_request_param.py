import os
import random

def generate_app_nonce() -> int:
    """
    Generates a random 3-byte AppNonce (as integer).
    LoRaWAN spec: AppNonce is little-endian when serialized, but stored as int.
    """
    return random.getrandbits(24)  # 3-byte int


def generate_device_addr(nwk_id: int, nwk_addr: int) -> bytes:
    """
    Generates a 4-byte DevAddr based on NetID and NwkAddr.
    Format: [NwkID (7 bits) | NwkAddr (25 bits)]
    Follows LoRaWAN Addr format for Class A devices.

    Args:
        nwk_id: 7-bit or 3-byte network identifier (e.g. 0x12)
        nwk_addr: 25-bit device-specific network address (e.g. 0x34567)

    Returns:
        4-byte DevAddr (in little endian)
    """
    # Ensure NwkID fits 7 bits and NwkAddr fits 25 bits
    if nwk_id > 0x7F or nwk_addr > 0x1FFFFFF:
        raise ValueError("Invalid NwkID or NwkAddr size")

    dev_addr_int = ((nwk_id & 0x7F) << 25) | (nwk_addr & 0x1FFFFFF)
    return dev_addr_int.to_bytes(4, "little")


def generate_dl_settings(rx1_offset: int = 0, rx2_dr: int = 0) -> int:
    """
    Generates the DLSettings byte:
    Bits 7-4: RFU (0)
    Bits 3-1: RX1DROffset (3 bits)
    Bit 0: RX2DataRate (4 bits)

    Default: RX1Offset = 0, RX2DataRate = 0
    """
    if not (0 <= rx1_offset <= 7 and 0 <= rx2_dr <= 15):
        raise ValueError("RX1 offset must be [0–7], RX2 DR must be [0–15]")
    return (rx1_offset << 4) | (rx2_dr & 0x0F)


def generate_rx_delay(rx_delay: int = 1) -> int:
    """
    Generates the RxDelay byte. 1 = 1 second.
    """
    if not (1 <= rx_delay <= 15):
        raise ValueError("RxDelay must be between 1 and 15 (seconds)")
    return rx_delay


def generate_cf_list() -> bytes:
    """
    Generates CFList for EU868: list of 5 optional channel frequencies (3 bytes each)
    Total size: 16 bytes (15 for channels, 1 RFU at end)

    LoRaWAN 1.0.3: frequencies are in Hz and must be divisible by 100
    """
    # Define 5 custom channels (optional), in Hz
    channel_frequencies_hz = [
        867100000, 867300000, 867500000,
        867700000, 867900000
    ]

    cf_bytes = bytearray()
    for freq in channel_frequencies_hz:
        freq_value = int(freq / 100)  # Convert to 100Hz units
        cf_bytes += freq_value.to_bytes(3, "little")  # Little-endian 3 bytes

    # Add 1-byte RFU (must be 0x00)
    cf_bytes += b"\x00"

    return bytes(cf_bytes)
