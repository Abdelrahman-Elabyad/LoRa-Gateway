
import binascii

#General CRC verification function
def verify_crc(Input_Bytes, received_crc):
    return binascii.crc_hqx(Input_Bytes, 0x0000) == received_crc

#For the 2 CRCs in the PHDR and PHY payload
def Physical_Layer_CRC_Checker(phdr, phdr_crc, phy_payload, payload_crc):
    return verify_crc(phdr, phdr_crc) and verify_crc(phy_payload, payload_crc)