#This can be used to genrate the downlink mac commands

elif direction == 1:  # Downlink from gateway
        match cid:
            
            case 0x82:  # LinkCheckAns
                if len(payload) == 2:
                    output["Fields"] = {
                        "Margin": payload[0],            # Link margin (0..254 dB)
                        "GwCnt": payload[1]              # Number of gateways received last uplink
                    }
                else:
                    output["Fields"] = {"Error": "Malformed payload (expected 2 bytes)"}
            
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