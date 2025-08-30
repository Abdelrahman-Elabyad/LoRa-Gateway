import base64
import json
from typing import Dict

import base64

def downlink_wrap_pkt_into_json(payload_bytes: bytes, freq: float, rfch: int, powe: int,
                                modu: str, datr: str, codr: str, ipol: bool, tmst: int) -> dict:
    """
    Build a txpk JSON for Semtech UDP forwarder. Force safe values for fields
    that uplink metadata doesn’t provide correctly.
    """
    txpk = {
        "tmst": tmst,
        "freq": float(freq),            # keep same freq unless you explicitly switch to RX2
        "rfch": 0,                      # hard-coded: downlinks TX on chain 0
        "powe": 14,                     # hard-coded: 14 dBm (safe EU868 default)
        "modu": "LORA",                 # always LoRa
        "datr": datr,                   # from uplink or RX2 plan
        "codr": "4/5",                  # safe default
        "ipol": True,                   # must be True for downlink
        "size": len(payload_bytes),
        "data": base64.b64encode(payload_bytes).decode("utf-8"),
    }
    return {"txpk": txpk}



