import os
import yaml
from datetime import datetime
from NS_shim.time_stamp import compute_rx_timestamps

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


def get_app_key(dev_eui,config_path="config/network_server_device_config.yaml"):

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
    Loads AppNonce, NetID, and latest DevNonce from a device YAML file.

    Args:
        dev_eui: DevEUI in LSB hex format (e.g., '0807060504030201')
        yaml_dir: Directory where the device YAMLs are stored

    Returns:
        Tuple of (AppNonce, NetID, DevNonce) all as bytes
    """
    yaml_path = os.path.join(yaml_dir, f"device_{dev_eui}.yaml")

    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"❌ YAML file for {dev_eui} not found at {yaml_path}")

    with open(yaml_path, "r", encoding="utf-8") as f:
        device_data = yaml.safe_load(f)

    try:
        # Convert AppNonce from decimal string to 3-byte little-endian
        app_nonce = int(device_data["AppNonce"]).to_bytes(3, "little")

        # Convert NetID from decimal string to 3-byte little-endian
        net_id = int(device_data["NetID"]).to_bytes(3, "little")

        # Convert latest DevNonce from hex string to bytes
        dev_nonce_list = device_data.get("DevNonces", [])
        if not dev_nonce_list:
            raise ValueError("❌ DevNonce list is empty.")
        dev_nonce = bytes.fromhex(dev_nonce_list[-1])  # 2 bytes

    except KeyError as e:
        raise ValueError(f"❌ Missing key in device YAML: {e}")
    except Exception as e:
        raise ValueError(f"❌ Error parsing YAML for {dev_eui}: {e}")

    return app_nonce, net_id, dev_nonce


def get_network_ids(dev_eui: str, config_path: str = "config/network_server_device_config.yaml") -> tuple[int, int]:
    """
    Retrieves NwkID and NwkAddr for a given DevEUI from a central registry YAML file.

    Args:
        dev_eui: DevEUI in hex string format (LSB, as stored in devices_eui)
        config_path: Path to the central device registry YAML file

    Returns:
        Tuple (nwk_id, nwk_addr) as integers
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"❌ Registry file not found at {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        registry = yaml.safe_load(f)

    devices = registry.get("devices_eui", {})
    dev_info = devices.get(dev_eui.upper())

    if not dev_info:
        raise ValueError(f"❌ DevEUI {dev_eui} not found in central registry.")

    try:
        nwk_id = int(dev_info["NwkID"])
        nwk_addr = int(dev_info["NwkAddr"])
    except KeyError as e:
        raise ValueError(f"❌ Missing field {e} in device {dev_eui}")
    except ValueError:
        raise ValueError(f"❌ NwkID or NwkAddr for {dev_eui} is not a valid integer.")

    return nwk_id, nwk_addr


def get_device_session_keys(dev_eui, output_dir="device_config"):
    """
    Loads a device's YAML config and returns the NwkSKey and AppSKey.
    """
    yaml_path = os.path.join(output_dir, f"device_{dev_eui}.yaml")

    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"❌ YAML file for DevEUI {dev_eui} not found at {yaml_path}")

    with open(yaml_path, "r") as file:
        data = yaml.safe_load(file)

    nwk_skey = data.get("NwkSKey")
    app_skey = data.get("AppSKey")

    if nwk_skey is None or app_skey is None:
        raise KeyError(f"❌ One or both session keys (NwkSKey, AppSKey) are missing in the YAML for DevEUI {dev_eui}")

    return nwk_skey, app_skey


def store_devaddr_to_deveui_mapping(dev_addr: str, dev_eui: str, index_file="config/DevAddrToDevEUI.yaml"):
    """
    Stores a mapping of DevAddr to DevEUI in a central YAML file 
    to be used later on as teh packets later are only identified using dev_addr.
    """
    # Normalize input (always upper-case hex)
    dev_addr = dev_addr.upper()
    dev_eui = dev_eui.upper()

    # Ensure config file exists
    if os.path.exists(index_file):
        with open(index_file, "r") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    # Ensure "DevAddrToDevEUI" section exists
    if "DevAddrToDevEUI" not in data:
        data["DevAddrToDevEUI"] = {}

    # Update the mapping
    data["DevAddrToDevEUI"][dev_addr] = dev_eui

    # Write back to the YAML file
    with open(index_file, "w") as f:
        yaml.safe_dump(data, f)

    print(f"✅ Stored mapping: DevAddr {dev_addr} → DevEUI {dev_eui}")


def get_dev_eui_from_dev_addr(dev_addr, mapping_file="config/DevAddrToDevEUI.yaml"):
    """
    Returns the DevEUI corresponding to a given DevAddr from the mapping file.
    """
    dev_addr = dev_addr.upper()

    if not os.path.exists(mapping_file):
        raise FileNotFoundError(f"Mapping file not found: {mapping_file}")

    with open(mapping_file, "r") as f:
        data = yaml.safe_load(f) or {}

    dev_eui = data.get("DevAddrToDevEUI", {}).get(dev_addr)

    if dev_eui is None:
        raise KeyError(f"DevAddr {dev_addr} not found in mapping.")

    return dev_eui


# Note : teh device yaml file should be deleted after disconnection i.e before another join request and should be go back to default setup settings
def delete_device_yaml_file(dev_eui, output_dir="device_config"):
    """
    Deletes the YAML configuration file for a given DevEUI if it exists.
    """
    yaml_path = os.path.join(output_dir, f"device_{dev_eui}.yaml")

    if os.path.exists(yaml_path):
        try:
            os.remove(yaml_path)
            print(f"✅ Device YAML file deleted: {yaml_path}")
            return True
        except Exception as e:
            print(f"❌ Error deleting file {yaml_path}: {e}")
            return False
    else:
        print(f"⚠️ Device YAML file not found: {yaml_path}")
        return False

def update_network_server_yaml_file(tmst: int, state_path: str = "config/network_server_device_config.yaml") -> None:
    """
    Stores gateway scheduling metadata at the network-server level.
    - tmst: concentrator timestamp used for the *last scheduled downlink*.

    File layout (config/network_server_state.yaml):
      LastDownlinkTMST: <int>
      TMSTHistory: [ ... ]          # optional rolling history (last 10)
      LastUpdated: <ISO8601Z>
    """
    # Ensure parent dir exists
    os.makedirs(os.path.dirname(state_path) or ".", exist_ok=True)

    # Load existing state or initialize
    if os.path.exists(state_path):
        with open(state_path, "r", encoding="utf-8") as f:
            state = yaml.safe_load(f) or {}
    else:
        state = {}

    # Update fields
    state["LastDownlinkTMST"] = int(tmst)
    history = state.get("TMSTHistory", [])
    history.append(int(tmst))
    # Keep only the last 10 entries to avoid unbounded growth
    state["TMSTHistory"] = history[-10:]
    state["LastUpdated"] = datetime.utcnow().isoformat() + "Z"

    # Write back
    with open(state_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(state, f, sort_keys=False)

    print(f"✅ Network server state updated at {state_path} (LastDownlinkTMST={tmst})")

################################## STORE META DATA FROM JSON OBJECT ######################################

def _parse_lora_datr(datr: str | None):
    # "SF7BW125" -> (7, 125)
    if not isinstance(datr, str): return None, None
    s = datr.upper()
    try:
        if "SF" in s and "BW" in s:
            sf = int(s.split("SF")[1].split("BW")[0])
            bw = int(s.split("BW")[1])
            return sf, bw
    except Exception:
        pass
    return None, None

def store_uplink_meta_from_push(dev_eui: str, push_data: dict, output_dir: str = "device_config") -> None:
    """
    Persist *all* useful rxpk fields + computed RX1/RX2 TMST to device_<DevEUI>.yaml.

    YAML layout (under .Meta):
      LastUplink:   full primary rxpk + parsed SF/BW + gateway_eui (if present)
      RX1_TMST, RX2_TMST
      UplinkHistory: last 20 snapshots (time, tmst, freq, datr, rssi, lsnr, chan, rfch, size, codr)
      AllRxpk: last 5 full rxpk entries (verbatim)
      LastSeenAt, LastUpdated
    """
    os.makedirs(output_dir, exist_ok=True)
    yaml_path = os.path.join(output_dir, f"device_{dev_eui}.yaml")
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"❌ Device YAML for {dev_eui} not found at {yaml_path}")

    with open(yaml_path, "r", encoding="utf-8") as f:
        dev = yaml.safe_load(f) or {}

    dev.setdefault("Meta", {})
    meta = dev["Meta"]

    rxpks = push_data.get("rxpk") or push_data.get("RXPK") or []
    if not isinstance(rxpks, list) or not rxpks:
        # touch heartbeat only
        meta["LastSeenAt"] = datetime.utcnow().isoformat() + "Z"
        dev["LastUpdated"] = meta["LastSeenAt"]
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(dev, f, sort_keys=False)
        print(f"⚠️ No rxpk in PUSH_DATA for {dev_eui}.")
        return

    rx0 = dict(rxpks[0])  # canonical
    sf, bw_khz = _parse_lora_datr(rx0.get("datr"))

    # prefer DeviceSettings.RX1Delay, else top-level RxDelay, else 1s
    rx1_delay = (
        dev.get("DeviceSettings", {}).get("RX1Delay")
        or dev.get("RxDelay")
        or 1
    )
    try:
        rx1_delay = int(rx1_delay)
    except Exception:
        rx1_delay = 1

    # RX2 delay: if you store RX2 in YAML, prefer it; else default to RX1+1s
    rx2_delay = dev.get("DeviceSettings", {}).get("RX2Delay")  # optional in your schema
    if rx2_delay is not None:
        try:
            rx2_delay = int(rx2_delay)
        except Exception:
            rx2_delay = None  # fall back to RX1+1 below

    # ✅ use your function
    rx1_tmst, rx2_tmst = compute_rx_timestamps(
        uplink_tmst=rx0.get("tmst"),
        rx1_delay_s=rx1_delay,
        rx2_delay_s=rx2_delay,
    )

    gw_eui = push_data.get("gateway_eui") or push_data.get("mac") or push_data.get("eui")

    # Full LastUplink block
    last_uplink = {
        **rx0,
        "SF": sf,
        "BW_kHz": bw_khz,
    }
    if gw_eui:
        last_uplink["gateway_eui"] = gw_eui

    meta["LastUplink"] = last_uplink
    meta["RX1_TMST"] = rx1_tmst
    meta["RX2_TMST"] = rx2_tmst

    # Rolling compact history (last 20)
    hist = meta.get("UplinkHistory", [])
    for r in rxpks:
        hist.append({
            "time": r.get("time"),
            "tmst": r.get("tmst"),
            "freq": r.get("freq"),
            "chan": r.get("chan"),
            "rfch": r.get("rfch"),
            "rssi": r.get("rssi"),
            "lsnr": r.get("lsnr"),
            "datr": r.get("datr"),
            "codr": r.get("codr"),
            "size": r.get("size"),
        })
    meta["UplinkHistory"] = hist[-20:]

    # Keep the last 5 full rxpk entries verbatim
    all_rxpk = meta.get("AllRxpk", [])
    all_rxpk.extend(rxpks)
    meta["AllRxpk"] = all_rxpk[-5:]

    meta["LastSeenAt"] = datetime.utcnow().isoformat() + "Z"
    dev["LastUpdated"] = meta["LastSeenAt"]

    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(dev, f, sort_keys=False)

    print(f"✅ Stored full PUSH_DATA metadata for {dev_eui} → {yaml_path}")

def add_metadata_to_device_yaml(dev_eui: str, metadata: dict, output_dir="device_config"):
    """
    Overwrites the 'Metadata' section in the device YAML with the latest radio metadata.
    Example metadata dict: {"tmst": 12345, "freq": 868100000, "dr": "SF7BW125", "rssi": -45, "snr": 5.5}
    """
    yaml_path = os.path.join(output_dir, f"device_{dev_eui}.yaml")

    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"❌ Device YAML for {dev_eui} not found at {yaml_path}")

    with open(yaml_path, "r") as f:
        device_data = yaml.safe_load(f) or {}

    # Always overwrite with latest metadata
    device_data["Metadata"] = metadata

    with open(yaml_path, "w") as f:
        yaml.dump(device_data, f, sort_keys=False)

    print(f"✅ Updated metadata for {dev_eui}: {yaml_path}")

#later when the ADR is setup we can also add teh datar in teh meta data under downlink so taht we can update it in teh packet entry point
def get_meta_data_from_device_yaml(meta_data: dict):
    """
    Unpacks radio metadata dictionary into individual variables.

    Expected keys in `meta_data`:
      - tmst, freq, rfch, powe, modu, datr, codr, ipol
    Also reads DLSettings if available:
      - DLSettings.RX1Delay, DLSettings.RX2DataRate, DLSettings.RX2Freq

    Returns:
      (tmst, freq, rfch, powe, modu, datr, codr, ipol, rx1_delay, rx2_datr, rx2_freq)
    """
    if not isinstance(meta_data, dict):
        raise TypeError("meta_data must be a dict")

    tmst = meta_data.get("tmst")
    freq = meta_data.get("freq")
    rfch = meta_data.get("rfch")
    powe = meta_data.get("powe")   # optional
    modu = meta_data.get("modu")
    datr = meta_data.get("datr")
    codr = meta_data.get("codr")
    ipol = meta_data.get("ipol")

    dl_settings = meta_data.get("DLSettings", {})
    rx1_tmst = dl_settings.get("rx1_tmst")
    rx2_tmst = dl_settings.get("rx2_tmst")

    return tmst, freq, rfch, powe, modu, datr, codr, ipol, rx1_tmst, rx2_tmst

