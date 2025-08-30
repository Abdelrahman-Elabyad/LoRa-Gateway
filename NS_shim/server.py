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
    """Bind to UDP and process Semtech UDP packets."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((CFG["SERVER_IP"], CFG["UDP_PORT"]))

    print(f"[NS] Listening on {CFG['SERVER_IP']}:{CFG['UDP_PORT']} "
          f"(→ default gw {CFG['GATEWAY_IP']}:{CFG['UDP_PORT']})")

    # Remember the most recent PULL_DATA sender to reply PULL_RESP there
    last_pull_addr = None

    while True:
        last_pull_addr = receive_uplink(sock, last_pull_addr)


def receive_uplink(sock: socket.socket, last_pull_addr) -> tuple[str, int] | None:
    try:
        data, addr = sock.recvfrom(CFG['BUF_SIZE'])
        if len(data) < 4:
            print("[NS] Packet too short!")
            return last_pull_addr

        ver = data[0]
        token = data[1:3]
        pkt_type = data[3]
        mac = data[4:12] if len(data) >= 12 else b""

        print(f"[NS] RX type=0x{pkt_type:02X} from {addr}, ver={ver}, token={token.hex()}, MAC={mac.hex()}")

        if pkt_type == 0x00:  # PUSH_DATA
            # Body starts at byte 12
            try:
                msg = json.loads(data[12:].decode("utf-8"))
                print("[NS] PUSH_DATA JSON:", msg)

                # Process uplink and maybe build a downlink JSON {"txpk": {...}}
                try:
                    downlink_json = handle_uplink_packet(msg)
                    if downlink_json:
                        # Prefer replying to the most recent PULL_DATA addr (if available)
                        target_addr = last_pull_addr or (CFG["GATEWAY_IP"], CFG["UDP_PORT"])
                        send_pull_resp(sock, downlink_json, target_addr)
                except Exception as e:
                    print("[NS] Uplink handler error:", e)

                # Send PUSH_ACK
                push_ack = bytearray([ver, token[0], token[1], 0x01])  # 0x01 = PUSH_ACK
                sock.sendto(push_ack, addr)
                print("[NS] PUSH_ACK sent")

            except Exception as e:
                print("[NS] PUSH_DATA invalid JSON:", e)

        elif pkt_type == 0x02:  # PULL_DATA (gateway keepalive / TX channel)
            # Reply PULL_ACK and remember addr for PULL_RESP
            pull_ack = bytearray([ver, token[0], token[1], 0x04])  # 0x04 = PULL_ACK
            sock.sendto(pull_ack, addr)
            print("[NS] PULL_ACK sent")
            last_pull_addr = addr

        elif pkt_type == 0x05:  # TX_ACK
            # May include optional JSON after 12 bytes
            payload = data[12:].decode("utf-8", errors="ignore")
            print("[NS] TX_ACK:", payload if payload else "<no body>")

        else:
            print(f"[NS] Unknown packet type: 0x{pkt_type:02X}")

        return last_pull_addr

    except Exception as e:
        print("[NS] Receive error:", e)
        return last_pull_addr


def send_pull_resp(sock: socket.socket, down_json: Dict[str, Any], addr: tuple[str, int]) -> None:
    """
    Send a Semtech PULL_RESP:
      [ver][tokenH][tokenL][0x03] + JSON
    The token is arbitrary per frame.
    """
    try:
        # Minimal txpk hygiene (avoid None values)
        txpk = down_json.get("txpk", {})
        txpk.setdefault("rfch", 0)
        txpk.setdefault("powe", 14)
        txpk.setdefault("modu", "LORA")
        txpk.setdefault("codr", "4/5")
        txpk.setdefault("ipol", True)
        down_json["txpk"] = txpk

        payload = json.dumps(down_json, separators=(",", ":")).encode("utf-8")

        # Random token for this PULL_RESP
        rtok = os.urandom(2)
        frame = bytearray([0x01, rtok[0], rtok[1], 0x03])  # 0x03 = PULL_RESP
        frame += payload

        sock.sendto(frame, addr)
        print(f"[NS] PULL_RESP sent → {addr}")

    except Exception as e:
        print("[NS] Downlink send error:", e)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    start_server()
