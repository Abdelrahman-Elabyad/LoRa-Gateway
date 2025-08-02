from parsing.data_uplink_handler import parse_data_up_packet

def test_data_up_valid_packet():
    # Dummy MHDR = 0x40, DevAddr = 01020304, FCnt = 0001, FPort = 01
    # MACPayload = FHDR + FPort + FRMPayload
    # MIC = DEADBEEF (fake)
    mtype = 2
    mhdr = {"MType": 2, "RFU": 0, "Major": 0}
    mhdr_byte = bytes([0x40])
    mic = bytes.fromhex("6513DB90")

    mac_payload = bytes.fromhex("04030201A000001" + "AA")

    result = parse_data_up_packet(mtype, mhdr, mhdr_byte, mic, mac_payload)

    assert result["DevAddr"] == int.from_bytes(bytes.fromhex("04030201"), "little")
    assert result["FPort"] == 1
    assert result["FRMPayload"] == b"\xAA"
