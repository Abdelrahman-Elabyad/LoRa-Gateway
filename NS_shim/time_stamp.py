import json
import base64
"""
Notes:
- The 'tmst' field represents the microsecond counter when the first symbol of the uplink arrived.
- RX1 and RX2 receive windows are calculated as offsets from 'tmst':
    RX1 start = tmst + (RX1Delay in seconds × 1,000,000)
    RX2 start = RX1 start + 1,000,000 (default 1s later)
"""


def fetch_pkt_timestamp():
    # Load JSON file
    with open("NS_shim/push_data.json", "r") as f:
        push_data = json.load(f)

    # Extract concentrator timestamp
    uplink_tmst = push_data["rxpk"][0]["tmst"]
    return uplink_tmst
    
    
def compute_rx_timestamps(uplink_tmst: int, rx1_delay_s: int, rx2_delay_s: int | None):
    MICROSECONDS = 1_000_000
    TMST_MAX = 2**32  # concentrator 32-bit wrap
    if rx2_delay_s is None:
        rx2_delay_s = rx1_delay_s + 1
    rx1_tmst = (uplink_tmst + rx1_delay_s * MICROSECONDS) % TMST_MAX
    rx2_tmst = (uplink_tmst + rx2_delay_s * MICROSECONDS) % TMST_MAX
    return rx1_tmst, rx2_tmst

    
