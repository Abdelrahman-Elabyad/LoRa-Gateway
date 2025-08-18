import json
import base64

def lora_packet_extractor(push_data_json: dict) -> bytes:
    """
    Accepts the JSON object you received over UDP and returns raw PHYPayload bytes.
    Supports both:
      - Semtech UDP format: {"rxpk":[{"data":"<base64>"}]}
      - Your own shim:      {"type":"uplink","phy":"<base64>"}
    """
    if not isinstance(push_data_json, dict):
        raise TypeError("push_data_json must be a dict")

    # Case A: Semtech UDP JSON from packet forwarder (rxpk list)
    if "rxpk" in push_data_json:
        rxpk_list = push_data_json.get("rxpk") or []
        if not rxpk_list:
            raise ValueError("No rxpk entries found")
        data_b64 = rxpk_list[0].get("data")
        if not data_b64:
            raise ValueError("rxpk[0].data is missing")
        return base64.b64decode(data_b64)
    
    raise ValueError("Unsupported uplink JSON shape (expected 'rxpk' or {'type':'uplink','phy':...})")


