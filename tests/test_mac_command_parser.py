from processing.mac_cmd_processing import process_mac_commands

def test_mac_commands_in_fopts():
    # MAC commands: CID=0x02 (LinkCheckReq) in FOpts, FPort ≠ 0
    parsed = {
        "FOpts": bytes.fromhex("02"),
        "FOptsLen": 1,
        "FPort": 1,
        "FRMPayload": b"",
        "DevAddr": b"\x01\x02\x03\x04",
        "FCnt": 1,
        "MType": 2
    }
    result = process_mac_commands(parsed)
    assert result[0]["CID"] == "0x02"
    assert "LinkCheckReq" in result[0]["Name"]
