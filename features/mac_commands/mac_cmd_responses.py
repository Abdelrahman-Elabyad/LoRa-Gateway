
#Need to

def analyze_mac_commands(mac_command_list: list[dict]) -> list[str]:
    """
    Analyzes a list of MAC command dictionaries and returns a list of action messages.
    Each command must contain: CID (e.g. "0x03"), Name, and Fields.

    Returns a list of strings describing required actions or none needed.
    """
    actions = []

    for cmd in mac_command_list:
        cid = cmd["CID"]
        name = cmd["Name"]
        fields = cmd.get("Fields", {})

        match cid:
            # 0x02 - LinkCheckReq (uplink)
            case "0x02":
                actions.append("📡 LinkCheckReq received → Send LinkCheckAns in next downlink.")

            # 0x03 - LinkADRAns (uplink)
            case "0x03":
                ch_ack = fields.get("ChMaskACK")
                dr_ack = fields.get("DataRateACK")
                tx_ack = fields.get("TxPowerACK")

                if all([ch_ack, dr_ack, tx_ack]):
                    actions.append("✅ LinkADRAns: All settings accepted → No action needed.")
                else:
                    details = []
                    if not ch_ack:
                        details.append("❌ ChMask rejected")
                    if not dr_ack:
                        details.append("❌ DataRate rejected")
                    if not tx_ack:
                        details.append("❌ TxPower rejected")
                    actions.append(f"⚠️ LinkADRAns: Some settings rejected ({', '.join(details)}) → Consider retrying LinkADRReq.")

            # 0x04 - DutyCycleAns (uplink)
            case "0x04":
                actions.append("✅ DutyCycleAns: Device accepted duty cycle limits → No action needed.")

            # 0x05 - RXParamSetupAns (uplink)
            case "0x05":
                freq_ack = fields.get("FreqACK")
                rx2_ack = fields.get("RX2DRAck")
                rx1_ack = fields.get("RX1OffsetACK")

                if all([freq_ack, rx2_ack, rx1_ack]):
                    actions.append("✅ RXParamSetupAns: All parameters accepted.")
                else:
                    details = []
                    if not freq_ack:
                        details.append("❌ RX2 frequency rejected")
                    if not rx2_ack:
                        details.append("❌ RX2 data rate rejected")
                    if not rx1_ack:
                        details.append("❌ RX1 offset rejected")
                    actions.append(f"⚠️ RXParamSetupAns: Some parameters rejected ({', '.join(details)}) → Consider resending RXParamSetupReq.")

            # 0x06 - DevStatusAns (uplink)
            case "0x06":
                battery = fields.get("BatteryLevel")
                snr = fields.get("SNRMargin")
                actions.append(f"🔋 DevStatusAns received → Battery: {battery}, SNR Margin: {snr} dB → Log or adapt ADR if needed.")

            case _:
                actions.append(f"❓ Unknown or unhandled MAC command: CID {cid} ({name})")
            case "0x07":
                freq_ack = fields.get("FrequencyACK")
                dr_range_ack = fields.get("DRRangeACK")

                if freq_ack and dr_range_ack:
                    actions.append("✅ NewChannelAns: Frequency and DR range accepted.")
                else:
                    reasons = []
                    if not freq_ack:
                        reasons.append("❌ Frequency rejected")
                    if not dr_range_ack:
                        reasons.append("❌ DR range rejected")
                    actions.append(f"⚠️ NewChannelAns: Some settings rejected ({', '.join(reasons)}) → Consider resending NewChannelReq.")

            # 0x08 - RXTimingSetupAns
            case "0x08":
                actions.append("✅ RXTimingSetupAns received → Device accepted new RX1 delay.")

            # 0x09 - TxParamSetupAns
            case "0x09":
                actions.append("✅ TxParamSetupAns received → Device accepted new TX power constraints.")

            # 0x0A - DlChannelAns
            case "0x0A":
                freq_ack = fields.get("FreqACK")
                ch_idx_ack = fields.get("ChannelIndexACK")
                if freq_ack and ch_idx_ack:
                    actions.append("✅ DlChannelAns: Downlink channel and index accepted.")
                else:
                    reasons = []
                    if not freq_ack:
                        reasons.append("❌ Frequency rejected")
                    if not ch_idx_ack:
                        reasons.append("❌ Channel index rejected")
                    actions.append(f"⚠️ DlChannelAns: Some settings rejected ({', '.join(reasons)}) → Consider retrying DlChannelReq.")

    return actions
