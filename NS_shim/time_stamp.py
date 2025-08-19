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

def decide_receive_window(uplink_rx_time: float, rx1_tmst: int, rx2_tmst: int) -> int:
    """
    Determines which RX window is active based on time elapsed since uplink reception.

    Args:
        uplink_rx_time (float): The system clock (time.perf_counter()) at which uplink was received.
        rx1_tmst (int): TMST value scheduled for RX1.
        rx2_tmst (int): TMST value scheduled for RX2.

    Returns:
        int: The TMST of the window that is active now. Choose RX1 if still in RX1 window, else RX2.
    """
    if rx1_tmst is None or rx2_tmst is None:
        raise ValueError("Missing RX1/RX2 tmst values")

    TMST_TICKS_PER_SEC = 1_000_000  # TMST is in microseconds

    # How many microseconds since the uplink arrived?
    elapsed_us = int((time.perf_counter() - uplink_rx_time) * TMST_TICKS_PER_SEC)

    # Assume uplink TMST was t0, so now = t0 + elapsed_us
    current_tmst = (rx1_tmst - 1_000_000) + elapsed_us

    # Choose RX1 if still before RX2
    if current_tmst < rx2_tmst:
        return rx1_tmst
    else:
        return rx2_tmst

