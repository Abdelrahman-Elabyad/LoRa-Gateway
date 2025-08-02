from construct import Struct, Byte, Bytes, Int32ul
from processing.device_registry import genrate_update_device_yaml_file
JoinAcceptPayload = Struct(
    "AppNonce" / Bytes(3),
    "NetID" / Bytes(3),
    "DevAddr" / Bytes(4),
    "DLSettings" / Byte,
    "RxDelay" / Byte,
    "MIC" / Bytes(4)  # This is added after MIC calculation
)


def Join_accept_builder(dev_eui, app_eui, dev_nonce, net_id, dev_addr, dl_settings, rx_delay):
    
    