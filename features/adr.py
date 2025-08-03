# LoRa network allows the end-devices to individually use any of the possible data rates. This
# feature is used by the LoRaWAN to adapt and optimize the data rate of static end-devices.
# This is referred to as Adaptive Data Rate (ADR) and when this is enabled the network will be
# optimized to use the fastest data rate possible.
# Adaptive Data Rate control may not be possible when the radio channel attenuation changes
# fast and constantly. When the network is unable to control the data rate of a device, the
# device’s application layer should control it. It is recommended to use a variety of different data
# rates in this case. The application layer should always try to minimize the aggregated air time
# used given the network conditions.

# If the ADR bit is set, the network will control the data rate of the end-device through the
# appropriate MAC commands. If the ADR bit is not set, the network will not attempt to control
# the data rate of the end-device regardless of the received signal quality. The ADR bit MAY be
# set and unset by the end-device or the Network on demand. However, whenever possible, the
# ADR scheme should be enabled to increase the battery life of the end-device and maximize
# the network capacity.

#Prototype to check if ADR is enabled and take action accordingly
def is_adr_enabled(parsed_frame):
    adr = parsed_frame["FCtrl"]["ADR"]
    if (adr==1):
        print("Network / gateway willl control the data rate of the end-device through the appropriate MAC commands.")
    else:
        print("Network / gateway will not attempt to control the data rate of the end-device regardless of the received signal quality.")
    
