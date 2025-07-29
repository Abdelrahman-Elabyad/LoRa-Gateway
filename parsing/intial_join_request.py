import os
import yaml
from construct import Struct, Bytes 
from features.security import device_yaml_path_exists_with_devnonce
#According to the lorawan Specification 1.0.3 
#the device already has DEVEUI and APPEUI and AppKey set up Before the Join request is sent 
    #DevEUI is a gloabl unique identifier for the device in IEEE EUI-64 format
    #AppEUI is a globally unique identifier for the application in IEEE EUI-64 format
    #AppKey is a 128-BIT AES encryption key used for securing the join procedure and subsequent communication

def parse_join_request(Packet_Data: bytes, output_dir="device_config"):
    """
    Parses a Join Request and writes YAML only if DevNonce is new for this device.
    """
    JoinRequestFrame = Struct(
        "AppEUI" / Bytes(8),
        "DevEUI" / Bytes(8),
        "DevNonce" / Bytes(2)
    )
    parsed = JoinRequestFrame.parse(Packet_Data)

    appeui = parsed.AppEUI.hex().upper()
    deveui = parsed.DevEUI.hex().upper()
    devnonce = parsed.DevNonce.hex().upper()

    # 🛡️ Efficiently check for DevNonce only in this device's YAML file
    existing = device_yaml_path_exists_with_devnonce(devnonce, deveui, output_dir)
    if existing:
        raise ValueError(f"❌ Duplicate Join Request for DevEUI {deveui}: DevNonce {devnonce} already used.")

    # ✅ Create/update YAML
    os.makedirs(output_dir, exist_ok=True)
    yaml_path = os.path.join(output_dir, f"device_{deveui}.yaml")

    if not os.path.exists(yaml_path):
        device_data = {
            "DevEUI": deveui,
            "AppEUI": appeui,
            "DevNonce": devnonce,
            "JoinStatus": "Pending"
        }
        with open(yaml_path, "w") as f:
            yaml.dump(device_data, f, sort_keys=False)

    return {
        "AppEUI": appeui,
        "DevEUI": deveui,
        "DevNonce": devnonce
    }


def Join_Request_Processing(Packet_Data: bytes):
    """
    Processes a Join Request packet.
    
    Args:
        Packet_Data (bytes): The raw packet data.
    
    Returns:
        dict: Parsed fields from the Join Request packet.
    """
    # Parse the packet data
    parsed_packet = parse_full_lorawan_frame(Packet_Data)
    
    # Extract relevant fields
    dev_eui = parsed_packet.get("DevEUI")
    app_eui = parsed_packet.get("AppEUI")
    app_key = parsed_packet.get("AppKey")
    
    if not dev_eui or not app_eui or not app_key:
        raise ValueError("Join Request must contain DevEUI, AppEUI, and AppKey.")
    
    # Return the parsed fields
    return {
        "DevEUI": dev_eui,
        "AppEUI": app_eui,
        "AppKey": app_key,
        "MType": parsed_packet["MType"]
    }
def create_device_yaml(MType, dev_addr, mac_commands):
    """
    Create or update a device YAML file based on the MType and MAC commands.
    
    :param MType: The message type of the LoRaWAN packet.
    :param dev_addr: The device address.
    :param mac_commands: The MAC commands to be processed.
    """
    if MType in [0, 1]:  # Join Request or Join Accept
        print(f"Skipping MAC command processing for MType {MType}.")
        return

    # Process MAC commands and update YAML
    update_device_yaml(mac_commands, dev_addr)