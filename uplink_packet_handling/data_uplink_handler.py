from protocol_layers.application_layer import parse_app_layer
from features.security import compute_verify_mic
from uplink_packet_handling.processing.device_registry import get_device_session_keys,get_dev_eui_from_dev_addr

def handle_data_uplink(mtype: int, mhdr: dict, mhdr_byte: bytes, mic: bytes, mac_payload: bytes):
    """
    Parses and validates Unconfirmed or Confirmed Data Up packets.
    Returns a flat dictionary structure.
    """
    
    app_result = parse_app_layer(mac_payload)
    devaddr = app_result["FHDR"]["DevAddr"]
    counter = app_result["FHDR"]["FCnt"]
    dev_eui=get_dev_eui_from_dev_addr(devaddr)
    nwk_skey,app_skey= get_device_session_keys(dev_eui)
    valid = compute_verify_mic(nwk_skey,devaddr,counter,0,mhdr_byte,mac_payload,mic)

    if not valid:
        raise ValueError("❌ Invalid MIC in DataUp")

    mic_value = int.from_bytes(mic, "little") if isinstance(mic, (bytes, bytearray)) else mic

    return {
        "Type": "UnconfirmedDataUp" if mtype == 2 else "ConfirmedDataUp",
        "MHDR": mhdr,
        "MType": mhdr["MType"],
        "RFU": mhdr["RFU"],
        "Major": mhdr["Major"],
        "MIC": mic_value,
        "DevAddr": app_result["FHDR"]["DevAddr"],
        "FCtrl": app_result["FHDR"]["FCtrl"],
        "FCnt": int.from_bytes(app_result["FHDR"]["FCnt"], "little") if isinstance(app_result["FHDR"]["FCnt"], (bytes, bytearray)) else app_result["FHDR"]["FCnt"],
        "FOpts": app_result["FHDR"]["FOpts"],
        "FPort": app_result["FPort"],
        "FRMPayload": app_result["FRMPayload"],
        "ADR": app_result["FHDR"]["FCtrl"]["ADR"],
        "ADRACKReq": app_result["FHDR"]["FCtrl"]["ADRACKReq"],
        "ACK": app_result["FHDR"]["FCtrl"]["ACK"],
        "ClassB": app_result["FHDR"]["FCtrl"]["ClassB"],
        "FOptsLen": app_result["FHDR"]["FCtrl"]["FOptsLen"]
    }
