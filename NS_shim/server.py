import os
import json
import base64
import socket
import yaml
from typing import Optional, Callable, Dict, Any
from packet_handling.uplink_packet_entry_point import handle_uplink_packet  


# ---------- CORE FUNCTIONS ----------
def start_server(build_downlink: Optional[Callable[[Dict[str, Any], Any], Optional[Dict[str, Any]]]] = None) -> None:
    """
    Bind to UDP and process incoming uplinks.
    Optionally, pass build_downlink(msg, result) -> down_json to construct a downlink dynamically.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((CFG["SERVER_IP"], CFG["UDP_PORT"]))
    print(f"[NS] Listening on {CFG['SERVER_IP']}:{CFG['UDP_PORT']} (→ gateway {CFG['GATEWAY_IP']}:{CFG['UDP_PORT']})")

    while True:
        receive_uplink(sock, build_downlink=build_downlink)


def receive_uplink(sock: socket.socket, build_downlink: Optional[Callable[[Dict[str, Any], Any], Optional[Dict[str, Any]]]] = None) -> None:
    """
    Receive one UDP datagram, validate JSON uplink, run pipeline, and optionally send a downlink.
    """
    try:
        data, addr = sock.recvfrom(CFG["BUF_SIZE"])
    except Exception as e:
        print("[NS] recv error:", e)
        return

    try:
        msg = json.loads(data.decode())
    except Exception as e:
        print("[NS] Bad JSON:", e)
        return

    if msg.get("type") != "uplink" or "phy" not in msg:
        print("[NS] Ignoring non-uplink JSON")
        return

    try:
        phy_bytes = base64.b64decode(msg["phy"])
    except Exception as e:
        print("[NS] Bad base64 in 'phy':", e)
        return

    # ---- your LoRaWAN processing pipeline ----
    try:
        result = handle_uplink_packet(phy_bytes)
    except Exception as e:
        print("[NS] Processing error:", e)
        return

    # Option A: Caller supplied a builder to decide if/how to reply
    down_json = None
    if callable(build_downlink):
        try:
            down_json = build_downlink(msg, result)
        except Exception as e:
            print("[NS] downlink builder error:", e)

    # Option B: Or the sender included an explicit downlink payload in the uplink message
    if down_json is None:
        down_json = msg.get("downlink")

    if down_json:
        send_downlink(sock, down_json)


def send_downlink(sock: socket.socket, down_json: Dict[str, Any]) -> None:
    """
    Send a JSON downlink to the gateway (Pi) using settings from YAML.

    Expected minimal shape:
      {
        "type": "downlink",
        "phy": "<base64>",        # PHYPayload to transmit
        "tmst": 123456789,        # concentrator timestamp for RX1/RX2
        "rfch": 0,
        "freq": 868100000,
        "dr": "SF7BW125"
      }

    You can add any extra fields your gateway stub/forwarder expects.
    """
    try:
        payload = json.dumps(down_json).encode()
        sock.sendto(payload, (CFG["GATEWAY_IP"], CFG["UDP_PORT"]))
        print("[NS] Downlink sent → gateway")
    except Exception as e:
        print("[NS] Downlink send error:", e)


