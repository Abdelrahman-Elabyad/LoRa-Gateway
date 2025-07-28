from helper_main    import handle_lorawan_packet
from config.settings import SAMPLE_PACKET_BYTES, NWK_SKEY, APP_SKEY
from features.security import decrypt_frm_payload
def main():
    print("Packet length:", len(SAMPLE_PACKET_BYTES))
    print("Packet hex:", SAMPLE_PACKET_BYTES.hex().upper())
    decrypt_frm_payload(
    app_skey=APP_SKEY,
    nwkskey=NWK_SKEY,
    dev_addr=...,
    fcnt=...,
    direction=0,
    frm_payload=bytes.fromhex("340B9EA26C"),
    Fport=0
)

    handle_lorawan_packet(SAMPLE_PACKET_BYTES)

if __name__ == "__main__":
    main()