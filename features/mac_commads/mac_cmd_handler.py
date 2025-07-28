def handle_mac_command_by_cid(commands: dict, index: int,direction )-> dict:
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
                output["Fields"] = {
                "Request": "LinkCheckReq: Device is asking for link quality feedback."
            }

            case 0x03:  # LinkADRAns
                if len(payload) == 1:
                    output["Fields"] = {
                        "ChMaskACK": bool(payload[0] & 0x01),
                        "DataRateACK": bool((payload[0] >> 1) & 0x01),
                        "TxPowerACK": bool((payload[0] >> 2) & 0x01)
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload"}

            case 0x04:  # DutyCycleAns
                output["Fields"] = {
                    "Ack": True
                }

            case 0x05:  # RXParamSetupAns
                if len(payload) == 1:
                    status = payload[0]
                    output["Fields"] = {
                        "FreqACK": bool((status >> 2) & 0x01),
                        "RX2DRAck": bool((status >> 1) & 0x01),
                        "RX1OffsetACK": bool(status & 0x01)
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload"}

            case 0x06:  # DevStatusAns
                if len(payload) == 2:
                    battery = payload[0]
                    margin = int.from_bytes(payload[1:2], "little", signed=True)
                    output["Fields"] = {
                        "BatteryLevel": battery,
                        "SNRMargin": margin
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload"}

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

            case 0x8F:  # RejoinParamSetupAns
                if len(payload) == 1:
                    output["Fields"] = {
                        "RejoinACK": bool(payload[0] & 0x01),
                        "MaxCountACK": bool((payload[0] >> 1) & 0x01),
                        "MaxTimeACK": bool((payload[0] >> 2) & 0x01)
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload"}


    elif direction == 1:  # Downlink from gateway
        match cid:
            case 0x03:  # LinkADRReq
                if len(payload) == 4:
                    output["Fields"] = {
                        "DataRate": (payload[0] >> 4) & 0x0F,
                        "TxPower": payload[0] & 0x0F,
                        "ChMask": f"0x{int.from_bytes(payload[1:3], 'little'):04X}",
                        "NbTrans": payload[3]
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload"}

            case 0x04:  # DutyCycleReq
                if len(payload) == 1:
                    max_duty = payload[0] & 0x0F
                    output["Fields"] = {
                        "MaxDutyCycle": f"1/{2**max_duty}"
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload"}

            case 0x05:  # RXParamSetupReq
                if len(payload) == 4:
                    output["Fields"] = {
                        "RX1DROffset": (payload[0] >> 4) & 0x0F,
                        "RX2DataRate": payload[0] & 0x0F,
                        "Frequency": int.from_bytes(payload[1:4], "little") * 100
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload"}

            case 0x06:  # DevStatusReq
                output["Fields"] = {
                    "Request": "DevStatusReq: Gateway is requesting battery and margin status."
                }

            case 0x07:  # NewChannelReq
                if len(payload) == 5:
                    ch_index = payload[0]
                    freq = int.from_bytes(payload[1:4], "little") * 100
                    dr_range = payload[4]
                    output["Fields"] = {
                        "ChannelIndex": ch_index,
                        "Frequency": freq,
                        "MinDataRate": dr_range & 0x0F,
                        "MaxDataRate": (dr_range >> 4) & 0x0F
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload"}

            case 0x08:  # RXTimingSetupReq
                if len(payload) == 1:
                    output["Fields"] = {
                        "RX1Delay": payload[0] & 0x0F
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload"}

            case 0x09:  # TxParamSetupReq
                if len(payload) == 1:
                    dwell = (payload[0] >> 4) & 0x03
                    output["Fields"] = {
                        "MaxEIRPIndex": payload[0] & 0x0F,
                        "UplinkDwellTime": bool(dwell & 0x01),
                        "DownlinkDwellTime": bool((dwell >> 1) & 0x01)
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload"}

            case 0x0A:  # DlChannelReq
                if len(payload) == 4:
                    output["Fields"] = {
                        "ChannelIndex": payload[0],
                        "DownlinkFrequency": int.from_bytes(payload[1:4], "little") * 100
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload"}

            case 0x0B:  # RekeyInd
                if len(payload) == 1:
                    output["Fields"] = {
                        "LoRaWANVersion": payload[0]
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload"}

            case 0x0C:  # ADRParamSetupReq
                if len(payload) == 1:
                    output["Fields"] = {
                        "ADR_ACK_Delay": payload[0] & 0x0F,
                        "ADR_ACK_Limit": (payload[0] >> 4) & 0x0F
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload"}

            case 0x0D:  # DeviceTimeReq
                output["Fields"] = {
                    "Request": "DeviceTimeReq: Gateway is requesting the device to sync GPS time."
                }

            case 0x0E:  # ForceRejoinReq
                if len(payload) == 2:
                    output["Fields"] = {
                        "RejoinType": payload[0] & 0x03,
                        "MaxRetries": (payload[0] >> 2) & 0x07,
                        "RejoinPeriodSeconds": payload[1]
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload"}

            case 0x0E:  # RejoinParamSetupReq
                if len(payload) == 1:
                    output["Fields"] = {
                        "MaxTimeExponent": payload[0] & 0x3F,
                        "MaxCountExponent": (payload[0] >> 6) & 0x03
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload"}
    else:
        output["Fields"] = {"Error": "Unknown direction"}
    return output