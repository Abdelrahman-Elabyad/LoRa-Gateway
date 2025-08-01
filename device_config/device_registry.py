import os
import yaml

def store_join_request_metadata(dev_eui: str, app_eui: str, dev_nonce: str, output_dir="device_config"):
    """
    Stores join request metadata in a YAML file for the given DevEUI.
    Ensures that DevNonce is not reused (replay attack prevention).
    """
    os.makedirs(output_dir, exist_ok=True)
    yaml_path = os.path.join(output_dir, f"device_{dev_eui}.yaml")

    device_data = {}

    if os.path.exists(yaml_path):
        with open(yaml_path, "r") as f:
            device_data = yaml.safe_load(f) or {}

        # Ensure 'DevNonces' list exists
        if "DevNonces" not in device_data:
            device_data["DevNonces"] = []

        # Check for duplicate DevNonce
        if dev_nonce in device_data["DevNonces"]:
            raise ValueError(f"❌ Duplicate DevNonce '{dev_nonce}' for DevEUI {dev_eui}")

        device_data["DevNonces"].append(dev_nonce)

    else:
        # First-time device registration
        device_data = {
            "DevEUI": dev_eui,
            "AppEUI": app_eui,
            "DevNonces": [dev_nonce],
            "JoinStatus": "Pending"
        }

    # Write to YAML
    with open(yaml_path, "w") as f:
        yaml.dump(device_data, f, sort_keys=False)
