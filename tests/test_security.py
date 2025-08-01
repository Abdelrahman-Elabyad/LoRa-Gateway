from features.security import compute_join_request_mic

def test_join_request_mic():
    app_key = bytes.fromhex("000102030405060708090A0B0C0D0E0F")
    payload = bytes.fromhex("00" + "1122334455667788" + "8877665544332211" + "AABB")
    mic = compute_join_request_mic(app_key, payload)
    assert isinstance(mic, bytes)
    assert len(mic) == 4
