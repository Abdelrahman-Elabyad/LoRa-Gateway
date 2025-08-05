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


def update_device_yaml_with_join_parameters(dev_eui, params, output_dir="device_config"):
    """
    Updates the device YAML file with join-accept parameters:
    AppNonce, DevAddr, NetID, DLSettings, RxDelay, CFList.
    """
    yaml_path = os.path.join(output_dir, f"device_{dev_eui}.yaml")

    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"❌ Device YAML for {dev_eui} not found at {yaml_path}")

    with open(yaml_path, "r") as f:
        device_data = yaml.safe_load(f) or {}

    # Update fields from params
    device_data.update({
        "AppNonce": params["AppNonce"].hex().upper() if isinstance(params["AppNonce"], bytes) else str(params["AppNonce"]),
        "DevAddr": params["DevAddr"].hex().upper(),
        "NetID": params["NetID"].hex().upper(),
        "DLSettings": params["DLSettings"],
        "RxDelay": params["RxDelay"],
        "CFList": [f"{b:02X}" for b in params["CFList"]],
        "LastUpdated": datetime.utcnow().isoformat() + "Z"
    })

    with open(yaml_path, "w") as f:
        yaml.dump(device_data, f, sort_keys=False)

    print(f"✅ Device YAML updated with join parameters: {yaml_path}")


def update_device_yaml_with_session_keys(dev_eui, nwk_skey, app_skey, output_dir="device_config"):
    """
    Updates the device YAML with session keys and final join status.
    All fields are stored at the top level of the YAML.
    """
    yaml_path = os.path.join(output_dir, f"device_{dev_eui}.yaml")

    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"❌ Device YAML for {dev_eui} not found at {yaml_path}")

    with open(yaml_path, "r") as f:
        device_data = yaml.safe_load(f) or {}

    device_data.update({
        "NwkSKey": nwk_skey.hex().upper(),
        "AppSKey": app_skey.hex().upper(),
        "JoinStatus": "Accepted",
        "FCntUp": 0,
        "FCntDown": 0,
        "LastUpdated": datetime.utcnow().isoformat() + "Z"
    })

    with open(yaml_path, "w") as f:
        yaml.dump(device_data, f, sort_keys=False)

    print(f"✅ Device YAML updated with session keys: {yaml_path}")


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


def get_app_key(dev_eui,config_path="config/sample_packet_config.yaml"):

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"❌ Registry file not found: {config_path}")

    with open(config_path, "r") as f:
        registry = yaml.safe_load(f)

    devices = registry.get("devices_eui", {})
    dev_info = devices.get(dev_eui.upper()) #returns the values if it finds it else returns none

    if not dev_info:
        raise ValueError(f"❌ DevEUI {dev_eui} not found in device registry.")

    app_key_hex = dev_info.get("AppKey")
    if not app_key_hex:
        raise ValueError(f"❌ AppKey missing for DevEUI {dev_eui}")

    app_key = bytes.fromhex(app_key_hex)

    return app_key


def get_appnonce_netid_devnonce(dev_eui: str, yaml_dir="device_config") -> tuple[bytes, bytes, bytes]:
    """
    Loads AppNonce, NetID, and latest DevNonce for a device from its YAML file.

    Returns:
        (app_nonce, net_id, dev_nonce) as byte values
    """
    yaml_path = os.path.join(yaml_dir, f"device_{dev_eui}.yaml")

    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"❌ YAML file for {dev_eui} not found in {yaml_dir}")

    with open(yaml_path, "r") as f:
        device_data = yaml.safe_load(f) or {}

    try:
        app_nonce = bytes.fromhex(device_data["AppNonce"])
        net_id = bytes.fromhex(device_data["NetID"])
        dev_nonce_list = device_data.get("DevNonces", [])
        if not dev_nonce_list:
            raise ValueError("❌ DevNonce list is empty.")
        dev_nonce = bytes.fromhex(dev_nonce_list[-1])  # Use the latest DevNonce
    except KeyError as e:
        raise ValueError(f"❌ Missing key in YAML: {e}")
    except Exception as e:
        raise ValueError(f"❌ Error parsing YAML for {dev_eui}: {e}")

    return app_nonce, net_id, dev_nonce


def get_network_ids(dev_eui: str, config_path="config/network_server_device_config.yaml") -> tuple[int, int]:
    """
    Retrieves NwkID and NwkAddr for a given DevEUI from the device config file.

    Args:
        dev_eui: DevEUI in hex string format
        config_path: Path to the device registry YAML file

    Returns:
        Tuple (nwk_id, nwk_addr) as integers
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"❌ Registry file not found at {config_path}")

    with open(config_path, "r") as f:
        registry = yaml.safe_load(f)

    devices = registry.get("devices_eui", {})
    dev_info = devices.get(dev_eui.upper())

    if not dev_info:
        raise ValueError(f"❌ DevEUI {dev_eui} not found in registry.")

    try:
        nwk_id = int(dev_info["NwkID"])
        nwk_addr = int(dev_info["NwkAddr"])
    except KeyError as e:
        raise ValueError(f"❌ Missing field {e} in device {dev_eui}")
    except ValueError:
        raise ValueError(f"❌ NwkID or NwkAddr for {dev_eui} is not a valid integer.")

    return nwk_id, nwk_addr
