from typing import List, Dict, Any, Optional

def build_downlink_plan_from_uplink(parsed_mac_cmds: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Consumes parsed uplink MAC commands (output of handle_uplink_mac_command_by_cid)
    and returns a downlink plan keyed by the response/request to send.
    Each case calls a dedicated per-command builder function you will define.

    Expected builder signatures (you'll implement them):
      - build_link_check_ans(fields: dict, index: int) -> Optional[dict]
      - build_link_adr_req(fields: dict, retry: dict, index: int) -> Optional[dict]
      - build_rx_param_setup_req(fields: dict, index: int) -> Optional[dict]
      - build_new_channel_req(fields: dict, retry: dict, index: int) -> Optional[dict]
      - build_dl_channel_req(fields: dict, retry: dict, index: int) -> Optional[dict]
      - build_device_time_ans(fields: dict, index: int) -> Optional[dict]

    Returned plan shape:
      {
        "LinkCheckAns": [ { ...job... }, ... ],
        "LinkADRReq":   [ { ...job... }, ... ],
        ...
      }
    Where each job is whatever your builder returns (e.g., {"Payload": "...", "Fields": {...}, ...})
    """
    plan: Dict[str, List[Dict[str, Any]]] = {}

    def add(key: str, job: Optional[Dict[str, Any]]):
        if job is not None:
            plan.setdefault(key, []).append(job)

    for cmd in parsed_mac_cmds:
        cid    = cmd.get("CID")            # e.g., "0x03"
        fields = cmd.get("Fields", {}) or {}
        idx    = cmd.get("Index")

        match cid:
            # Uplink 0x02 LinkCheckReq → respond with LinkCheckAns
            case "0x02":
                add("LinkCheckAns", build_link_check_ans(fields, idx))

            # Uplink 0x03 LinkADRAns → only retry for bits that were 0 (rejected)
            case "0x03":
                retry = {}
                if fields.get("ChMaskACK") is False:
                    retry["ChMask"] = True
                if fields.get("DataRateACK") is False:
                    retry["DataRate"] = True
                if fields.get("TxPowerACK") is False:
                    retry["TxPower"] = True
                if retry:
                    add("LinkADRReq", build_link_adr_req(fields, retry, idx))

            # Uplink 0x04 DutyCycleAns → no mandatory response (skip)

            # Uplink 0x05 RXParamSetupAns → if ANY bit is 0, device kept old values; retry is policy-driven
            case "0x05":
                rx1_ok = fields.get("RX1DROffsetACK") is True
                rx2_ok = fields.get("RX2DRAck")       is True
                ch_ok  = fields.get("ChannelACK")     is True
                if not (rx1_ok and rx2_ok and ch_ok):
                    add("RXParamSetupReq", build_rx_param_setup_req(fields, idx))

            # Uplink 0x06 DevStatusAns → no mandatory response (ADR policy may trigger later; skip here)

            # Uplink 0x07 NewChannelAns → only retry for failed bits
            case "0x07":
                retry = {}
                if fields.get("FrequencyACK") is False:
                    retry["Frequency"] = True
                if fields.get("DRRangeACK") is False:
                    retry["DRRange"] = True
                if retry:
                    add("NewChannelReq", build_new_channel_req(fields, retry, idx))

            # Uplink 0x08 RXTimingSetupAns → no mandatory response (skip)

            # Uplink 0x09 TxParamSetupAns → no mandatory response (skip)

            # Uplink 0x0A DlChannelAns → only retry for failed bits
            case "0x0A":
                retry = {}
                if fields.get("FreqACK") is False:
                    retry["DownlinkFrequency"] = True
                if fields.get("ChannelIndexACK") is False:
                    retry["ChannelIndex"] = True
                if retry:
                    add("DlChannelReq", build_dl_channel_req(fields, retry, idx))

            # Uplink 0x0D DeviceTimeReq → respond with DeviceTimeAns
            # (If your parser labeled it differently, still respond here based on CID)
            case "0x0D":
                add("DeviceTimeAns", build_device_time_ans(fields, idx))

            # RFU / unhandled in 1.0.3 → skip, or add diagnostics if you want
            case _:
                pass

    return plan
