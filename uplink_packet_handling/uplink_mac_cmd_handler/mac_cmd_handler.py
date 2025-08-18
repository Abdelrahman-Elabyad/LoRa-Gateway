from typing import Dict, Any, Optional

def handle_and_dispatch_uplink_mac_command(commands: Dict[str, Any], index: int, direction: int) -> Dict[str, Any]:
    """
    Merge of:
      - handle_uplink_mac_command_by_cid  (parses the uplink command into 'output')
      - build_downlink_plan_from_uplink   (pure dispatcher; no logic)

    Behavior:
      - Parses the given uplink MAC command (one item).
      - Immediately dispatches to the designated per-command builder with (fields, index).
      - No policy/bit checks here. Builders decide whether to return a job (or None).

    Returns:
      {
        "Parsed": <output dict with Fields>,
        "Plan": {
                "LinkCheckAns": ["020A03"],   # hex strings to send
                "LinkADRReq": ["03FF00..."],
                "DeviceTimeAns": ["0D0102030405"]
                }
      }
    """
    cid = int(commands["CID"], 16)
    name = commands["Name"]
    payload = bytes.fromhex(commands["Payload"]) if commands.get("Payload") else b""

    output = {
        "Index": index,
        "CID": f"0x{cid:02X}",
        "Name": name,
        "Fields": {}
    }

    plan: Dict[str, list] = {}

    def add(key: str, job: Optional[Any]):
        if job is not None:
            plan.setdefault(key, []).append(job)

    if direction == 0:  # Uplink from end device
        match cid:
            case 0x02:  # LinkCheckReq
                if len(payload) == 0:
                    output["Fields"] = {"Request": "LinkCheckReq"}
                else:
                    output["Fields"] = {"Error": "Malformed payload (expected 0 bytes)"}
                # pure dispatch
                add("LinkCheckAns", build_link_check_ans(output["Fields"], index))

            case 0x03:  # LinkADRAns
                if len(payload) == 1:
                    status = payload[0]
                    output["Fields"] = {
                        "ChMaskACK":  bool(status & 0x01),
                        "DataRateACK": bool((status >> 1) & 0x01),
                        "TxPowerACK":  bool((status >> 2) & 0x01)
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload (expected 1 byte)"}
                add("LinkADRReq", build_link_adr_req(output["Fields"], index))

            case 0x04:  # DutyCycleAns
                if len(payload) == 0:
                    output["Fields"] = {"Ack": True}
                else:
                    output["Fields"] = {"Error": "Malformed payload (expected 0 bytes)"}
                # usually no response; no dispatch

            case 0x05:  # RXParamSetupAns
                if len(payload) == 1:
                    status = payload[0]
                    output["Fields"] = {
                        "RX1DROffsetACK": bool(status & 0x01),
                        "RX2DRAck":       bool((status >> 1) & 0x01),
                        "ChannelACK":     bool((status >> 2) & 0x01)
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload (expected 1 byte)"}
                add("RXParamSetupReq", build_rx_param_setup_req(output["Fields"], index))

            case 0x06:  # DevStatusAns
                if len(payload) == 2:
                    battery = payload[0]
                    margin  = int.from_bytes(payload[1:2], "little", signed=True)
                    output["Fields"] = {
                        "BatteryLevel": battery,
                        "SNRMargin": margin
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload (expected 2 bytes)"}
                # usually policy-driven; no dispatch here

            case 0x07:  # NewChannelAns
                if len(payload) == 1:
                    output["Fields"] = {
                        "FrequencyACK": bool(payload[0] & 0x01),
                        "DRRangeACK":   bool((payload[0] >> 1) & 0x01)
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload (expected 1 byte)"}
                add("NewChannelReq", build_new_channel_req(output["Fields"], index))

            case 0x08:  # RXTimingSetupAns
                output["Fields"] = {"Ack": True}
                # usually no response; no dispatch

            case 0x09:  # TxParamSetupAns
                output["Fields"] = {"Ack": True}
                # usually no response; no dispatch

            case 0x0A:  # DlChannelAns
                if len(payload) == 1:
                    output["Fields"] = {
                        "FreqACK":         bool(payload[0] & 0x01),
                        "ChannelIndexACK": bool((payload[0] >> 1) & 0x01)
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload (expected 1 byte)"}
                add("DlChannelReq", build_dl_channel_req(output["Fields"], index))

            case 0x0B:  # RekeyConf (RFU in 1.0.3)
                output["Fields"] = {"RFU": True}
                # no dispatch

            case 0x0C:  # ADRParamSetupAns (RFU in 1.0.3)
                output["Fields"] = {"RFU": True}
                # no dispatch

            case 0x0D:  # DeviceTimeReq (uplink) OR DeviceTimeAns if you ever parse downlink
                if len(payload) == 0:
                    # Uplink DeviceTimeReq has 0B payload; respond with DeviceTimeAns
                    output["Fields"] = {"Request": "DeviceTimeReq"}
                elif len(payload) == 5:
                    # If you ever parse DeviceTimeAns uplink (non-standard); keep for completeness
                    output["Fields"] = {
                        "GPSTimeSeconds":   int.from_bytes(payload[0:4], "little"),
                        "FractionalSecond": payload[4]
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload (expected 0 or 5 bytes)"}
                add("DeviceTimeAns", build_device_time_ans(output["Fields"], index))

            case 0x0F:  # RejoinParamSetupAns (LoRaWAN 1.1; RFU in 1.0.3)
                if len(payload) == 1:
                    output["Fields"] = {
                        "RejoinACK":  bool(payload[0] & 0x01),
                        "MaxCountACK": bool((payload[0] >> 1) & 0x01),
                        "MaxTimeACK":  bool((payload[0] >> 2) & 0x01)
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload (expected 1 byte)"}
                # no dispatch in 1.0.3
    else:
        output["Fields"] = {"Error": "Wrong Direction supposed to be 0"}

    return {"Parsed": output, "Plan": plan}
