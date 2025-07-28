from helper_main    import handle_lorawan_packet
from config.settings import SAMPLE_PACKET_BYTES, NWK_SKEY, APP_SKEY
from features.security import decrypt_frm_payload

# Sample 16-byte session keys (hex or bytes). Must be exactly 16 bytes.
APP_SKEY = bytes.fromhex("2B7E151628AED2A6ABF7158809CF4F3C")
NWK_SKEY = bytes.fromhex("3B7E151628AED2A6ABF7158809CF4F3C")

# Sample DevAddr as integer (LoRaWAN uses 4 bytes, little-endian)
dev_addr = 0x26011BDA  # For example, can be replaced with any valid 4-byte int

# Frame counter (FCnt)
fcnt = 1  # or any other 2-byte counter value

# Direction: 0 = uplink, 1 = downlink
direction = 0

# Encrypted FRMPayload (from your example)
frm_payload = bytes.fromhex("340B9EA26C")

def main():
    SAMPLE_PACKET_BYTES = bytes.fromhex("40020100010500010305F201010148656C6C6F1B63C979")

    print("Packet length:", len(SAMPLE_PACKET_BYTES))
    print("Packet hex:", SAMPLE_PACKET_BYTES.hex().upper())

    decrypted = decrypt_frm_payload(
        app_skey=APP_SKEY,
        nwkskey=NWK_SKEY,
        dev_addr=dev_addr,
        fcnt=fcnt,
        direction=direction,
        frm_payload=frm_payload,
        Fport=0
    )

    print("Decrypted FRMPayload:", decrypted.hex().upper())


    handle_lorawan_packet(SAMPLE_PACKET_BYTES)

if __name__ == "__main__":
    main()