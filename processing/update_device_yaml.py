import yaml
import os
from datetime import datetime

def update_device_yaml(mac_commands: bytes, dev_addr):
    
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
    if isinstance(mac_commands, list):
        for cmd in mac_commands:
            for key, value in cmd.get("Fields", {}).items():
                device_yaml["Features"][key] = value
    else:
        print("⚠️ No valid MAC commands found. Skipping YAML write.")
        return


    device_yaml["LastUpdated"] = datetime.utcnow().isoformat() + "Z"

    # Step 5: Write back YAML
    with open(filename, "w") as file:
        yaml.dump(device_yaml, file, sort_keys=False)

    print(f"✅ Device YAML updated: {filename}")

