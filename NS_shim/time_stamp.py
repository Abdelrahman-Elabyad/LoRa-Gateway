import json
import base64
import time

MICROSECONDS = 1_000_000
TMST_MAX = 2**32

def compute_rx_tmsts(uplink_tmst: int, rx1_delay_s: int = 1, rx2_delay_s: int | None = None):
    if rx2_delay_s is None:
        rx2_delay_s = rx1_delay_s + 1
    rx1 = (uplink_tmst + rx1_delay_s * MICROSECONDS) % TMST_MAX
    rx2 = (uplink_tmst + rx2_delay_s * MICROSECONDS) % TMST_MAX
    return rx1, rx2

def choose_window_by_latency(
    recv_monotonic: float,
    rx1_delay_s: float = 1.0,
    rx2_delay_s: float | None = None,
    safety_margin_ms: int = 200,) -> str:
    """
    Decide RX1 or RX2 using your own elapsed processing time.
    - recv_monotonic: time.monotonic() captured when you received the uplink
    - safety_margin_ms: how early you want the gateway to receive PULL_RESP
    """
    if rx2_delay_s is None:
        rx2_delay_s = rx1_delay_s + 1

    elapsed_s = time.monotonic() - recv_monotonic
    # If we can still comfortably hit RX1, use it; otherwise RX2.
    return "RX1" if elapsed_s <= (rx1_delay_s - safety_margin_ms / 1000.0) else "RX2"

def decide_receive_window(NS_tmst: float, rx1_tmst: int, rx2_tmst: int, tx_time_us: int = 100_000) -> int:
    """
    Determines if RX1 can be used based on elapsed time and TX duration.
    Falls back to RX2 if not enough time remains to complete TX in RX1 window.

    Args:
        NS_tmst (float): time.perf_counter() at uplink arrival
        rx1_tmst (int): Scheduled RX1 timestamp (µs)
        rx2_tmst (int): Scheduled RX2 timestamp (µs)
        tx_time_us (int): Estimated airtime of downlink packet in µs (default: 100_000)

    Returns:
        int: Chosen TMST (rx1_tmst or rx2_tmst)
    """
    if rx1_tmst is None or rx2_tmst is None:
        raise ValueError("RX1 and RX2 TMST must not be None")

    TMST_TICKS_PER_SEC = 1_000_000

    # Elapsed time in microseconds
    elapsed_us = int((time.perf_counter() - NS_tmst) * TMST_TICKS_PER_SEC)

    # Uplink TMST ≈ rx1_tmst - 1 sec
    uplink_tmst = rx1_tmst - TMST_TICKS_PER_SEC
    current_tmst = uplink_tmst + elapsed_us

    # Ensure there's enough room to finish TX before RX2 starts
    if current_tmst + tx_time_us < rx2_tmst:
        return rx1_tmst
    else:
        return rx2_tmst



