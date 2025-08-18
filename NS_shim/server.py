import os
import json
import base64
import socket
from typing import Optional, Callable, Dict, Any
from uplink_packet_handling.uplink_packet_entry_point import handle_uplink_packet


# ---------------- CONFIG LOADING ----------------
def load_cfg(path: str = "config/network_server_config.json") -> Dict[str, Any]:

    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Config file not found at {path}")

    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    required = ["SERVER_IP", "UDP_PORT", "GATEWAY_IP", "BUF_SIZE"]
    for key in required:
        if key not in cfg:
            raise KeyError(f"❌ Missing required config key: {key}")

    return cfg

CFG = load_cfg()

# ---------------- CORE FUNCTIONS ----------------
def start_server() -> None:
    """Bind to UDP and process incoming uplinks."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((CFG["SERVER_IP"], CFG["UDP_PORT"]))

    print(f"[NS] Listening on {CFG['SERVER_IP']}:{CFG['UDP_PORT']} "
          f"(→ gateway {CFG['GATEWAY_IP']}:{CFG['UDP_PORT']})")

    while True:
        receive_uplink(sock)

def receive_uplink(sock: socket.socket) -> None:
    try:
        data, addr = sock.recvfrom(CFG["BUF_SIZE"])
    except Exception as e:
        print("[NS] recv error:", e); return

    # This is your incoming JSON object from the UDP forwarder/shim
    try:
        msg = json.loads(data.decode())
    except Exception as e:
        print("[NS] Bad JSON:", e); return

    # Give the ENTIRE object to the pipeline:
    try:
        downlink_json = handle_uplink_packet(msg)  # returns a dict or None
    except Exception as e:
        print("[NS] Processing error:", e); return

    if downlink_json:
        send_downlink(sock, downlink_json)


def send_downlink(sock: socket.socket, down_json: Dict[str, Any]) -> None:
    """Send a JSON downlink to the gateway."""
    try:
        payload = json.dumps(down_json).encode()
        sock.sendto(payload, (CFG["GATEWAY_IP"], CFG["UDP_PORT"]))
        print("[NS] Downlink sent → gateway")
    except Exception as e:
        print("[NS] Downlink send error:", e)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    start_server()
