import os
import yaml
from construct import Struct, Bytes 
from features.security import compute_verify_mic
#According to the lorawan Specification 1.0.3 
#the device already has DEVEUI and APPEUI and AppKey set up Before the Join request is sent 
    #DevEUI is a gloabl unique identifier for the device in IEEE EUI-64 format
    #AppEUI is a globally unique identifier for the application in IEEE EUI-64 format
    #AppKey is a 128-BIT AES encryption key used for securing the join procedure and subsequent communication

def parse_join_request(Packet_Data: bytes):

    JoinRequestFrame = Struct(
        "MHDR" / Bytes(1),  # MHDR byte
        "MacPayload" / Struct(
            "AppEUI" / Bytes(8),
            "DevEUI" / Bytes(8),
            "DevNonce" / Bytes(2)
        ),
        "MIC" / Bytes(4)  # Message Integrity Code
    )
    parsed = JoinRequestFrame.parse(Packet_Data)
    output_dir="device_config"
    # Extract fields
    mhdr = parsed.MHDR.hex().upper()
    mac_payload = parsed.MacPayload
    appeui = parsed.MacPayload.AppEUI.hex().upper()
    deveui = parsed.MacPayload.DevEUI.hex().upper()
    devnonce = parsed.MacPayload.DevNonce.hex().upper()
    mic = parsed.MIC.hex().upper()

    #MIC checker
    if not compute_verify_mic(mac_payload, mic):
        raise ValueError("Invalid MIC in Join Request")
    else:
        os.makedirs(output_dir, exist_ok=True)
        yaml_path = os.path.join(output_dir, f"device_{deveui}.yaml")

        device_data = {}

        if os.path.exists(yaml_path):
            with open(yaml_path, "r") as f:
                device_data = yaml.safe_load(f) or {}

            # Ensure 'DevNonces' list exists
            if "DevNonces" not in device_data:
                device_data["DevNonces"] = []

            # 🛑 Check if this DevNonce was already used (Avoid Replay Attacks)
            if devnonce in device_data["DevNonces"]:
                raise ValueError(f"❌ Duplicate DevNonce '{devnonce}' for DevEUI {deveui}")

            # ✅ Append new DevNonce
            device_data["DevNonces"].append(devnonce)

        else:
            # First time: initialize structure
            device_data = {
                "DevEUI": deveui,
                "AppEUI": appeui,
                "DevNonces": [devnonce],
                "JoinStatus": "Pending"
            }

        # Write updated YAML
        with open(yaml_path, "w") as f:
            yaml.dump(device_data, f, sort_keys=False)

        return {
            "AppEUI": appeui,
            "DevEUI": deveui,
            "DevNonce": devnonce
        }
