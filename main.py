import yaml
import os
from NS_shim.server import start_server
def main():

    with open("config/network_server_device_config.yaml","r",encoding="utf-8") as f:
        _C = yaml.safe_load(f) or {}
    for k in ("SERVER_IP","GATEWAY_IP","UDP_PORT","BUF_SIZE"):
        if k not in _C: raise KeyError(f"Missing {k} in YAML")
    SERVER_IP  = str(_C["SERVER_IP"])
    GATEWAY_IP = str(_C["GATEWAY_IP"])
    UDP_PORT   = int(_C["UDP_PORT"])
    BUF_SIZE   = int(_C["BUF_SIZE"])

    start_server()
    

if __name__ == "__main__":
    main()
