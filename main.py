from protocol_layers.frame_parser import parse_full_lorawan_frame


def main():
    # Example raw packet (hex string converted to bytes)
    sample_packet_hex = "00039F5C01123456789ABCDEF01234567890ABCD"
    packet_bytes = bytes.fromhex(sample_packet_hex)

    # Step 1: Parse all layers
    parsed_result = parse_full_lorawan_frame(packet_bytes)

    # Physical layer
    preamble     = parsed_result["preamble"]
    phdr         = parsed_result["PHDR"]
    phdr_crc     = parsed_result["PHDR_CRC"]
    phy_payload  = parsed_result["PHYPayload"]

    # MAC layer
    mhdr         = parsed_result["MHDR"]
    mtype        = parsed_result["MType"]
    rfu          = parsed_result["RFU"]
    major        = parsed_result["Major"]
    mac_payload  = parsed_result["MACPayload"]
    mic          = parsed_result["MIC"]

    # Application layer
    dev_addr     = parsed_result["DevAddr"]
    fctrl        = parsed_result["FCtrl"]
    fcnt         = parsed_result["FCnt"]
    fopts        = parsed_result["FOpts"]
    fport        = parsed_result["FPort"]
    frm_payload  = parsed_result["FRMPayload"]

    # Extract FCtrl flags
    adr          = fctrl["ADR"]
    adr_ack_req  = fctrl["ADRACKReq"]
    ack          = fctrl["ACK"]
    f_pending    = fctrl["FPending"]
    class_b      = fctrl["ClassB"]




if __name__ == "__main__":
    main()