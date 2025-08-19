import base64
import json
from typing import Dict

def downlink_wrap_pkt_into_json (lorawan_pkt_bytes,tmst: int,freq: int,rfch: int,powe: int,modu: str,datr: str,codr: str,ipol: bool) -> Dict:
    """
    Build JSON object for downlink.

    Parameters
    ----------
    phy_payload : bytes
        The raw PHYPayload (already encrypted + MIC).
    tmst : int
        Concentrator timestamp (from uplink + RX1/RX2 delay calculation).
    freq : int
        Frequency in Hz (e.g., 868100000).
    rfch : int
        RF chain index (typically 0).
    powe : int
        TX power in dBm (e.g., 14).
    modu : str
        Modulation ("LORA").
    datr : str
        Data rate (e.g., "SF7BW125").
    codr : str
        Coding rate (e.g., "4/5").
    ipol : bool
        Polarity inversion (True for Class A downlink).
    """

    return {
        "type": "downlink",
        "phy": base64.b64encode(lorawan_pkt_bytes).decode(),
        "tmst": tmst,
        "freq": freq,
        "rfch": rfch,
        "powe": powe if powe is not None else 14,
        "modu": modu,
        "datr": datr,
        "codr": codr,
        "ipol": ipol if ipol is not None else True,
        "size": len(lorawan_pkt_bytes)
    }

