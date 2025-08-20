import base64
import json
from typing import Dict

def downlink_wrap_pkt_into_json(payload_bytes: bytes,freq: float,rfch: int,powe: int, modu: str,datr: str,codr: str,ipol: bool,tmst: int ) -> dict:
    txpk = {
        "tmst": tmst,
        "freq": freq,
        "rfch": rfch,
        "powe": powe,
        "modu": modu,
        "datr": datr,
        "codr": codr,
        "ipol": ipol,
        "size": len(payload_bytes),
        "data": base64.b64encode(payload_bytes).decode("utf-8"),
        
    }
    return {"txpk": txpk}


