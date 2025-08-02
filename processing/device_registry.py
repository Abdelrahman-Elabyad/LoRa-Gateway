import os
import yaml
from datetime import datetime

def genrate_update_device_yaml_file(mac_command_features: list, dev_eui: str, app_eui: str, dev_nonce: str, output_dir="device_config"):
    """
    Creates or updates the device YAML configuration file.
    Adds DevNonce and integrates MAC command features into the 'Features' section.
    """
    os.makedirs(output_dir, exist_ok=True)
    yaml_path = os.path.join(output_dir, f"device_{dev_eui}.yaml")

    # Init or load YAML
    if os.path.exists(yaml_path):
        with open(yaml_path, "r") as f:
            device_data = yaml.safe_load(f) or {}

        # Initialize DevNonces if missing
        if "DevNonces" not in device_data:
            device_data["DevNonces"] = []

        # Check for duplicate DevNonce (replay attack)
        if dev_nonce in device_data["DevNonces"]:
            raise ValueError(f"❌ Duplicate DevNonce '{dev_nonce}' for DevEUI {dev_eui}")

        device_data["DevNonces"].append(dev_nonce)

        # Ensure Features exists
        if "Features" not in device_data:
            device_data["Features"] = {}

    else:
        # First time device registration
        device_data = {
            "DevEUI": dev_eui,
            "AppEUI": app_eui,
            "DevNonces": [dev_nonce],
            "JoinStatus": "Pending",
            "Features": {}
        }

    # ⬇️ Add or update MAC command features
    if isinstance(mac_command_features, list):
        for cmd in mac_command_features:
            fields = cmd.get("Fields", {})
            for key, value in fields.items():
                device_data["Features"][key] = value

    # Timestamp
    device_data["LastUpdated"] = datetime.utcnow().isoformat() + "Z"

    # Save back to YAML
    with open(yaml_path, "w") as f:
        yaml.dump(device_data, f, sort_keys=False)

    print(f"✅ Device YAML updated: {yaml_path}")
