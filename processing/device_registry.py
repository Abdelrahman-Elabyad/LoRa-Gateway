import os
import yaml
from datetime import datetime

def initialize_device_yaml(dev_eui, app_eui, dev_nonce, output_dir="device_config"):
    """
    Creates or updates the device YAML before sending Join-Accept.
    Checks for DevNonce reuse and initializes basic metadata.
    """
    os.makedirs(output_dir, exist_ok=True)
    yaml_path = os.path.join(output_dir, f"device_{dev_eui}.yaml")
    device_data = {}

    if os.path.exists(yaml_path):
        with open(yaml_path, "r") as f:
            device_data = yaml.safe_load(f) or {}

        if "DevNonces" not in device_data:
            device_data["DevNonces"] = []

        if dev_nonce in device_data["DevNonces"]:
            raise ValueError(f"❌ Duplicate DevNonce '{dev_nonce}' for DevEUI {dev_eui}")

        device_data["DevNonces"].append(dev_nonce)
    else:
        device_data = {
            "DevEUI": dev_eui,
            "AppEUI": app_eui,
            "DevNonces": [dev_nonce],
            "JoinStatus": "Pending",
            "Features": {}
        }

    device_data["LastUpdated"] = datetime.utcnow().isoformat() + "Z"

    with open(yaml_path, "w") as f:
        yaml.dump(device_data, f, sort_keys=False)

    print(f"✅ Initialized device YAML: {yaml_path}")


def finalize_device_yaml_with_keys(dev_eui, app_nonce, dev_addr, net_id, nwk_skey, app_skey, output_dir="device_config"):
    """
    Updates the device YAML with session keys and Join-Accept parameters.
    """
    yaml_path = os.path.join(output_dir, f"device_{dev_eui}.yaml")

    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"❌ Device YAML for {dev_eui} not found. Run initialization first.")

    with open(yaml_path, "r") as f:
        device_data = yaml.safe_load(f) or {}

    device_data.update({
        "AppNonce": app_nonce.hex().upper() if isinstance(app_nonce, bytes) else app_nonce,
        "DevAddr": dev_addr.hex().upper() if isinstance(dev_addr, bytes) else dev_addr,
        "NetID": net_id.hex().upper() if isinstance(net_id, bytes) else net_id,
        "NwkSKey": nwk_skey.hex().upper(),
        "AppSKey": app_skey.hex().upper(),
        "JoinStatus": "Accepted",
        "LastUpdated": datetime.utcnow().isoformat() + "Z"
    })

    with open(yaml_path, "w") as f:
        yaml.dump(device_data, f, sort_keys=False)

    print(f"✅ Finalized device YAML with session keys: {yaml_path}")


def update_device_yaml_with_mac_commands(dev_eui, mac_command_features, output_dir="device_config"):
    """
    Updates the device YAML with extracted MAC command features.
    """
    yaml_path = os.path.join(output_dir, f"device_{dev_eui}.yaml")

    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"❌ Device YAML for {dev_eui} not found. Cannot update MAC commands.")

    with open(yaml_path, "r") as f:
        device_data = yaml.safe_load(f) or {}

    if "Features" not in device_data:
        device_data["Features"] = {}

    if isinstance(mac_command_features, list):
        for cmd in mac_command_features:
            fields = cmd.get("Fields", {})
            for key, value in fields.items():
                device_data["Features"][key] = value

    device_data["LastUpdated"] = datetime.utcnow().isoformat() + "Z"

    with open(yaml_path, "w") as f:
        yaml.dump(device_data, f, sort_keys=False)

    print(f"✅ Updated device YAML with MAC command features: {yaml_path}")
