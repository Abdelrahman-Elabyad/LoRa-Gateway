from cryptography.hazmat.primitives.cmac import CMAC
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.backends import default_backend


def generate_lorawan_uplink_packet(dev_addr_hex, fcnt_hex, fport_hex, frmpayload_hex,
                                    nwk_skey_hex, mac_commands_hex=b"", confirmed=False):
    """
    Constructs a LoRaWAN Uplink packet from application layer downward.

    Parameters:
    - dev_addr_hex: 8-char hex string (little endian), e.g. "02010001"
    - fcnt_hex: 4-char hex string (2 bytes), e.g. "0001"
    - fport_hex: 2-char hex string, e.g. "01"
    - frmpayload_hex: hex string, e.g. "48656C6C6F" for "Hello"
    - nwk_skey_hex: 32-char hex string (16 bytes)
    - mac_commands_hex: hex string of optional FOpts MAC commands (unencrypted)
    - confirmed: bool, whether the packet is confirmed or unconfirmed data up

    Returns:
    - Final LoRaWAN packet hex string from MHDR to MIC
    """

    dev_addr = bytes.fromhex(dev_addr_hex)
    fcnt = bytes.fromhex(fcnt_hex)
    fport = bytes.fromhex(fport_hex)
    frmpayload = bytes.fromhex(frmpayload_hex)
    nwk_skey = bytes.fromhex(nwk_skey_hex)
    fopts = bytes.fromhex(mac_commands_hex) if mac_commands_hex else b""
    fopts_len = len(fopts)

    # MHDR
    mtype = 0x40 if not confirmed else 0x80  # Unconfirmed vs Confirmed Data Up
    mhdr = bytes([mtype])

    # FCtrl with FOptsLen
    fctrl_int = (0x00 & 0xF0) | fopts_len
    fctrl = bytes([fctrl_int])

    # FHDR
    fhdr = dev_addr + fctrl + fcnt + fopts

    # MACPayload = FHDR + FPort + FRMPayload
    mac_payload = fhdr + fport + frmpayload

    # B0 block for MIC
    def build_b0(dev_addr, fcnt, direction, msg_len):
        return bytes([
            0x49, 0x00, 0x00, 0x00, 0x00, 0x00,
            direction,
            *dev_addr,
            fcnt[0], fcnt[1], 0x00, 0x00,
            0x00,
            msg_len
        ])

    direction = 0  # uplink
    msg_len = len(mhdr + mac_payload)
    b0 = build_b0(dev_addr, fcnt, direction, msg_len)

    # MIC calculation
    cmac = CMAC(algorithms.AES(nwk_skey), backend=default_backend())
    cmac.update(b0 + mhdr + mac_payload)
    mic = cmac.finalize()[:4]

    # Final packet
    full_packet = mhdr + mac_payload + mic
    return full_packet.hex().upper()
