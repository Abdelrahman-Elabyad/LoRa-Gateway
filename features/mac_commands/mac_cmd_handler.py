def handle_uplink_mac_command_by_cid(commands: dict, index: int,direction )-> dict:
    cid = int(commands["CID"], 16)
    name = commands["Name"]
    payload = bytes.fromhex(commands["Payload"]) if commands["Payload"] else b""

    output = {
        "Index": index,
        "CID": f"0x{cid:02X}",
        "Name": name,
        "Fields": {}
    }
    
    if direction == 0:  # Uplink from end device
        match cid:
            case 0x02:  # LinkCheckReq
                if len(payload) == 0:
                    output["Fields"] = {
                        "Request": "LinkCheckReq: Device is asking for link quality feedback."
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload (expected 0 bytes)"}

            case 0x03:  # LinkADRAns
                if len(payload) == 1:
                    status = payload[0]
                    output["Fields"] = {
                        "ChMaskACK": bool(status & 0x01),
                        "DataRateACK": bool((status >> 1) & 0x01),
                        "TxPowerACK": bool((status >> 2) & 0x01)
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload (expected 1 byte)"}

            case 0x04:  # DutyCycleAns
                if len(payload) == 0:
                    output["Fields"] = {"Ack": True}
                else:
                    output["Fields"] = {"Error": "Malformed payload (expected 0 bytes)"}

            case 0x05:  # RXParamSetupAns
                if len(payload) == 1:
                    status = payload[0]
                    output["Fields"] = {
                        "RX1DROffsetACK": bool(status & 0x01),
                        "RX2DRAck": bool((status >> 1) & 0x01),
                        "ChannelACK": bool((status >> 2) & 0x01)
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload (expected 1 byte)"}

            case 0x06:  # DevStatusAns
                if len(payload) == 2:
                    battery = payload[0]
                    margin = int.from_bytes(payload[1:2], "little", signed=True)
                    output["Fields"] = {
                        "BatteryLevel": battery,
                        "SNRMargin": margin
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload (expected 2 bytes)"}

            case 0x07:  # NewChannelAns
                if len(payload) == 1:
                    output["Fields"] = {
                        "FrequencyACK": bool(payload[0] & 0x01),
                        "DRRangeACK": bool((payload[0] >> 1) & 0x01)
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload"}

            case 0x08:  # RXTimingSetupAns
                output["Fields"] = {
                    "Ack": True
                }

            case 0x09:  # TxParamSetupAns
                output["Fields"] = {
                    "Ack": True
                }

            case 0x0A:  # DlChannelAns
                if len(payload) == 1:
                    output["Fields"] = {
                        "FreqACK": bool(payload[0] & 0x01),
                        "ChannelIndexACK": bool((payload[0] >> 1) & 0x01)
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload"}

            case 0x0B:  # RekeyConf
                output["Fields"] = {
                    "RFU": True
                }

            case 0x0C:  # ADRParamSetupAns
                output["Fields"] = {
                    "RFU": True
                }

            case 0x0D:  # DeviceTimeAns
                if len(payload) == 5:
                    output["Fields"] = {
                        "GPSTimeSeconds": int.from_bytes(payload[0:4], "little"),
                        "FractionalSecond": payload[4]
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload"}

            case 0x0F:  # RejoinParamSetupAns
                if len(payload) == 1:
                    output["Fields"] = {
                        "RejoinACK": bool(payload[0] & 0x01),
                        "MaxCountACK": bool((payload[0] >> 1) & 0x01),
                        "MaxTimeACK": bool((payload[0] >> 2) & 0x01)
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload"}

    else:
        output["Fields"] = {"Error": "Wrong Direction supposed to be 0"}
    return output