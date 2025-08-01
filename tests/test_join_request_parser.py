from parsing.join_request_parser import parse_join_request

def test_join_request_parsing():
    packet_hex = "00" + "1122334455667788" + "8877665544332211" + "AABB" + "CCDD1122"
    packet = bytes.fromhex(packet_hex)
    result = parse_join_request(packet)
    
    assert result["MHDR"] == "00"
    assert result["AppEUI"] == "1122334455667788"
    assert result["DevEUI"] == "8877665544332211"
    assert result["DevNonce"] == "AABB"
    assert result["MIC"] == "CCDD1122"

