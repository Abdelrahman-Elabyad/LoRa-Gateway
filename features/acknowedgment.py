# When receiving a confirmed data message, the receiver SHALL respond with a data frame
# that has the acknowledgment bit (ACK) set. If the sender is an end-device, the network will
# send the acknowledgement using one of the receive windows opened by the end-device after
# the send operation. If the sender is a gateway, the end-device transmits an acknowledgment
# at its own discretion.
# Acknowledgements are only sent in response to the latest message received and are never
# retransmitted.

# Note: To allow the end-devices to be as simple as possible and have as
# few states as possible it may transmit an explicit (possibly empty)
# acknowledgement data message immediately after the reception of a
# data message requiring a confirmation. Alternatively the end-device may
# defer the transmission of an acknowledgement to piggyback it with its
# next data message.

#Prototype for the acknowledgment function
def send_acknowledgment(parsed_frame):
    """
    Function to send an acknowledgment for a confirmed data message.
    This function should be called in the RX1 or RX2 window after receiving a confirmed data message.
    """
    # Extract necessary information from the parsed frame
    dev_eui = parsed_frame["DevEUI"]
    app_eui = parsed_frame["AppEUI"]
    
    # Here you would implement the logic to send the acknowledgment
    # For example, you might use a LoRaWAN library to send a frame with ACK bit set
    print(f"✅ Acknowledgment sent for DevEUI: {dev_eui}, AppEUI: {app_eui}")