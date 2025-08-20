import time
from uplink_packet_handling.protocol_layers.mac_layer import parse_mac_layer
from uplink_packet_handling.dispatch_by_mtype import parse_lorawan_packet_by_type  
from NS_shim.uplink_gw_pkt__handler import lora_packet_extractor, extract_metadata_from_uplink
from NS_shim.time_stamp import compute_rx_tmsts

def handle_uplink_packet(push_data_json: dict):
    """
    Entry point: Parses any LoRaWAN uplink packet and returns:
      (result_summary, downlink_json_or_none)

    This version *only* computes RX1/RX2 tmst and forwards them;
    window selection is deferred to `dispatch_by_mtype`.
    """
    # 1) Extract raw bytes + metadata from the concentrator JSON
    lorawan_packet_bytes = lora_packet_extractor(push_data_json)
    meta_data = extract_metadata_from_uplink(push_data_json)  # should include 'tmst' (uplink)
    meta_data["recv_clock"] = time.perf_counter()
    # 2) Pre-compute RX1/RX2 tmst (no choice here)
    uplink_tmst = meta_data.get("tmst")
    if uplink_tmst is not None:
        rx1_tmst, rx2_tmst = compute_rx_tmsts(uplink_tmst, rx1_delay_s=1)
        # stash both for downstream decision
        meta_data["DLSettings"] = {
            "rx1_tmst": rx1_tmst,
            "rx2_tmst": rx2_tmst
        }
    else:
        meta_data["DlSettings"] = {"rx1_tmst": None, "rx2_tmst": None}

    # 3) Parse the LoRaWAN MAC
    mac_result = parse_mac_layer(lorawan_packet_bytes)

    # 4) Rebuild MHDR byte for downstream MIC logic
    mhdr = mac_result["MHDR"]
    mhdr_byte = bytes([
        (mhdr["MType"] & 0x07) |
        ((mhdr["RFU"] & 0x07) << 3) |
        ((mhdr["Major"] & 0x03) << 6)
    ])

    # 5) Dispatch by MType — pass meta_data (with dl_sched but no 'chosen')
    mtype = mhdr["MType"]
    mac_payload = mac_result["MACPayload"]
    mic = mac_result["MIC"]

    parse_lorawan_packet_by_type(mtype,lorawan_packet_bytes,mhdr,mhdr_byte,mac_payload,mic,meta_data)
    #downlink_json=parse_lorawan_packet_by_type(mtype,lorawan_packet_bytes,mhdr,mhdr_byte,mac_payload,mic,meta_data)
    
    #return downlink_json


    