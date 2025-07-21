from phy_layer import parse_phy_layer
from mac_layer import parse_mac_layer
from application_layer import parse_app_layer

def parse_full_lorawan_frame(Packet_Data: bytes):
    """
    Main parsing function that integrates physical, MAC, and app layer parsing.
    Takes in raw LoRaWAN byte data and returns structured dictionary of all layers.
    """

    # --- Physical Layer ---
    physical_result = parse_phy_layer(Packet_Data)
    physical_payload = physical_result["PHYPayload"]

    # --- MAC Layer ---
    mac_result = parse_mac_layer(physical_payload)
    mac_payload = mac_result["MACPayload"]
    
    # --- Application Layer ---
    app_result = parse_app_layer(mac_payload)
    
    # Combine all layers into one result
    return {
        "physical_layer": physical_result,
        "mac_layer": mac_result,
        "application_layer": app_result  
    }
