import yaml
import os
from datetime import datetime
from frame_parser import parse_full_lorawan_frame
from mac_cmd_processing import process_mac_commands

def generate_device_yaml(packet_data: bytes):
    # Step 1: Parse frame and get DevAddr
    parsed_frame = parse_full_lorawan_frame(packet_data)
    dev_addr_bytes = parsed_frame["application_layer"]["FHDR"]["DevAddr"]
    dev_addr = dev_addr_bytes.hex().upper()  # "26011BDA"

    # Step 2: Get MAC command results
    mac_commands = process_mac_commands(packet_data)
    if isinstance(mac_commands, dict) and "error" in mac_commands:
        print(f"Error: {mac_commands['error']}")
        return

    # Step 3: Load existing YAML (if exists)
    filename = f"device_{dev_addr}.yaml"
    if os.path.exists(filename):
        with open(filename, "r") as file:
            device_yaml = yaml.safe_load(file) or {}
    else:
        device_yaml = {}

    # Ensure required structure exists
    device_yaml["DevAddr"] = dev_addr
    if "Features" not in device_yaml:
        device_yaml["Features"] = {}

    # Step 4: Merge/Update new features
    for cmd in mac_commands:
        for key, value in cmd["Fields"].items():
            device_yaml["Features"][key] = value

    device_yaml["LastUpdated"] = datetime.utcnow().isoformat() + "Z"

    # Step 5: Write back YAML
    with open(filename, "w") as file:
        yaml.dump(device_yaml, file, sort_keys=False)

    print(f"✅ Device YAML updated: {filename}")

