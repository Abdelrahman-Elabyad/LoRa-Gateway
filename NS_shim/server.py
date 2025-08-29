import os
import json
import base64
import socket
from typing import  Dict, Any
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
        data, addr = sock.recvfrom(CFG['BUF_SIZE'])  # buffer size
        if len(data) < 4:
            print("[NS] Packet too short!")
            return

        protocol_version = data[0]
        rand_token = data[1:3]
        pkt_type = data[3]
        mac = data[4:12]

        # Debug print
        print(f"[NS] Received type=0x{pkt_type:02X} from {addr}, protocol_version={protocol_version}, rand_token={rand_token.hex()}, MAC={mac.hex()}")
        dispatch_using_pkt_type(pkt_type,sock,data,rand_token,addr)

    except Exception as e:
        print("[NS] Receive error:", e)

def dispatch_using_pkt_type(pkt_type,sock,data,rand_token,addr):
    if pkt_type == 0x00:  # Recieved PUSH_DATA
        try:
            json_str = data[12:].decode('utf-8')
            msg = json.loads(json_str)
            print("[NS] Valid PUSH_DATA with JSON:", msg)

            # 🔁 Process JSON (e.g., parse LoRaWAN uplink)
            try:
                downlink_json = handle_uplink_packet(msg)
                if downlink_json:
                    send_downlink(sock, downlink_json)
            except Exception as e:
                print("[NS] Uplink handler error:", e)

            # 🔁 Send PUSH_ACK
            push_ack = bytearray()
            push_ack.append(0x01)               # protocol protocol_version
            push_ack.extend(rand_token)         # same rand_token
            push_ack.append(0x01)               # PUSH_ACK
            sock.sendto(push_ack, addr)
            print("[NS] Sent PUSH_ACK")

        except Exception as e:
            print("[NS] PUSH_DATA invalid JSON:", e)

    elif pkt_type == 0x02:  # Recieved PULL_DATA
        pull_ack = bytearray()
        pull_ack.append(0x01)           # protocol protocol_version
        pull_ack.extend(rand_token)          # same rand_token
        pull_ack.append(0x04)           # PULL_ACK
        sock.sendto(pull_ack, addr)
        print("[NS] Sent PULL_ACK")

    elif pkt_type == 0x05:  # TX_ACK from gateway
        print("[NS] Received TX_ACK:", data[12:].decode("utf-8", errors="ignore"))

    else:
        print(f"[NS] Unknown packet type: 0x{pkt_type:02X}")

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
