from protocol_layers.application_layer import parse_app_layer
from features.security import compute_verify_mic
from config.settings import NWK_SKEY

def parse_data_up_packet(mtype: int, mhdr: dict, mhdr_byte: bytes, mic: bytes, mac_payload: bytes):
    """
    Parses and validates Unconfirmed or Confirmed Data Up packets.
    Returns a flat dictionary structure.
    """
    
    app_result = parse_app_layer(mac_payload)

    valid = compute_verify_mic(
        nwkskey=NWK_SKEY,
        dev_addr=app_result["FHDR"]["DevAddr"],
        fcnt=app_result["FHDR"]["FCnt"],
        direction=0,
        mhdr=mhdr_byte,
        payload=mac_payload,
        mic=mic
    )

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
