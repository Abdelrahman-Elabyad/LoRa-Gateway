from Proccessing.frame_parser import parse_full_lorawan_frame


#This fucntion should be used to help make descisions on how to interpret a packet recieved
def Mac_Commands_fetch(Mtype):
    """
    Determines the MAC commands based on the MType.
    """
    if Mtype == 0:  # Join Request
        return "Join Request MAC Command"
    elif Mtype == 1:  # Join Accept
        return "Join Accept MAC Command"
    elif Mtype == 2:  # Unconfirmed Data Up
        return "Unconfirmed Data Up MAC Command"
    elif Mtype == 3:  # Unconfirmed Data Down
        return "Unconfirmed Data Down MAC Command"
    elif Mtype == 4:  # Confirmed Data Up
        return "Confirmed Data Up MAC Command"
    elif Mtype == 5:  # Confirmed Data Down
        return "Confirmed Data Down MAC Command"
    elif Mtype == 6:  # RFU (Reserved for Future Use)
        return "Reserved for Future Use MAC Command"
    elif Mtype == 7:  # Proprietary
        return "Proprietary MAC Command"
    else:
        return "Unknown MType MAC Command"
