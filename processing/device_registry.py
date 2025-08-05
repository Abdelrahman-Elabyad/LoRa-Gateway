import os
import yaml
from datetime import datetime


def initialize_device_yaml(dev_eui, app_eui, dev_nonce, output_dir="device_config"):
    """
    Creates or updates the device YAML before sending Join-Accept.
    Checks for DevNonce reuse and initializes minimal structure.
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
        # New device
        device_data = {
            "DevEUI": dev_eui,
            "AppEUI": app_eui,
            "DevNonces": [dev_nonce],
            "JoinStatus": "Pending",
            "DevAddr": None,
            "AppSKey": None,
            "NwkSKey": None,
            "FCntUp": 0,
            "FCntDown": 0,
            "DeviceSettings": {
                "DataRate": None,
                "TxPower": None,
                "Channels": [],
                "RX1Delay": None,
                "RX2DataRate": None,
                "RX2Freq": None,
                "DutyCycle": None
            },
            "MACCommands": {},
            "Features": {}
        }

    device_data["LastUpdated"] = datetime.utcnow().isoformat() + "Z"

    with open(yaml_path, "w") as f:
        yaml.dump(device_data, f, sort_keys=False)

    print(f"✅ Initialized device YAML: {yaml_path}")


def update_device_yaml_with_session_keys(dev_eui, app_nonce, dev_addr, net_id, nwk_skey, app_skey, output_dir="device_config"):
    """
    Finalizes the device YAML with session keys and Join-Accept data.
    """
    yaml_path = os.path.join(output_dir, f"device_{dev_eui}.yaml")

    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"❌ Device YAML for {dev_eui} not found. check teh intailize yaml function?")

    with open(yaml_path, "r") as f:
        device_data = yaml.safe_load(f) or {}

    device_data.update({
        "AppNonce": app_nonce.hex().upper() if isinstance(app_nonce, bytes) else str(app_nonce),
        "DevAddr": dev_addr.hex().upper() if isinstance(dev_addr, bytes) else str(dev_addr),
        "NetID": net_id.hex().upper() if isinstance(net_id, bytes) else str(net_id),
        "NwkSKey": nwk_skey.hex().upper(),
        "AppSKey": app_skey.hex().upper(),
        "JoinStatus": "Accepted",
        "FCntUp": 0,
        "FCntDown": 0,
        "LastUpdated": datetime.utcnow().isoformat() + "Z"
    })

    with open(yaml_path, "w") as f:
        yaml.dump(device_data, f, sort_keys=False)

    print(f"✅ Finalized device YAML with session keys: {yaml_path}")


#This fucntion is used only to update the device settings if its required by the mac command
def update_device_yaml_settings_from_mac_cmds(dev_eui, settings_dict, output_dir="device_config"):
    yaml_path = os.path.join(output_dir, f"device_{dev_eui}.yaml")

    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"YAML for {dev_eui} not found.")

    with open(yaml_path, "r") as f:
        device_data = yaml.safe_load(f) or {}

    device_data.setdefault("DeviceSettings", {})

    # Apply updates
    for key, value in settings_dict.items():
        device_data["DeviceSettings"][key] = value

    device_data["LastUpdated"] = datetime.utcnow().isoformat() + "Z"

    with open(yaml_path, "w") as f:
        yaml.dump(device_data, f, sort_keys=False)

    print(f"✅ Device settings updated: {yaml_path}")


#need to be added after the parsing of a data up packet
def validate_and_update_fcnt_up(dev_eui, incoming_fcnt, output_dir="device_config"):
    """
    Validates the incoming FCntUp against the stored one.
    If valid (incoming > stored), updates the stored counter.
    Returns True if accepted, False if rejected.
    """
    yaml_path = os.path.join(output_dir, f"device_{dev_eui}.yaml")

    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"❌ Device YAML for {dev_eui} not found.")

    with open(yaml_path, "r") as f:
        device_data = yaml.safe_load(f) or {}

    stored_fcnt = device_data.get("FCntUp", 0)

    # Check: new FCnt must be strictly greater
    if incoming_fcnt > stored_fcnt:
        device_data["FCntUp"] = incoming_fcnt
        with open(yaml_path, "w") as f:
            yaml.dump(device_data, f, sort_keys=False)
        print(f"✅ FCntUp updated: {stored_fcnt} → {incoming_fcnt}")
        return True
    else:
        print(f"❌ Invalid FCntUp: {incoming_fcnt} ≤ stored {stored_fcnt}")
        return False
