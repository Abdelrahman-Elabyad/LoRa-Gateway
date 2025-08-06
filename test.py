from Crypto.Cipher import AES

def decrypt_join_accept_payload(encrypted_payload_hex, app_key_hex):
    encrypted_payload = bytes.fromhex(encrypted_payload_hex)
    app_key = bytes.fromhex(app_key_hex)

    # Step 1: Reverse
    reversed_payload = encrypted_payload[::-1]

    # Step 2: Pad to 16-byte boundary
    pad_len = (16 - len(reversed_payload) % 16) % 16
    reversed_padded = reversed_payload + b"\x00" * pad_len

    # Step 3: AES ECB decrypt
    cipher = AES.new(app_key, AES.MODE_ECB)
    decrypted_reversed = cipher.decrypt(reversed_padded)

    # Step 4: Reverse back and remove padding
    decrypted_payload = decrypted_reversed[::-1][:len(encrypted_payload)]

    return decrypted_payload

def parse_join_accept_fields(payload: bytes):
    print("\n📦 Parsed Join-Accept Payload Fields:")
    
    app_nonce = int.from_bytes(payload[0:3], "little")
    net_id    = int.from_bytes(payload[3:6], "little")
    dev_addr  = payload[6:10][::-1].hex().upper()
    dl_settings = payload[10]
    rx_delay = payload[11]
    cf_list = payload[12:28].hex().upper()

    print(f"🔑 AppNonce   : {app_nonce}")
    print(f"🌐 NetID      : {net_id} (0x{net_id:06X})")
    print(f"🆔 DevAddr    : {dev_addr}")
    print(f"⚙️  DLSettings : {dl_settings}")
    print(f"⏱️ RxDelay    : {rx_delay}")
    print(f"📶 CFList     : {cf_list[:30]}...")  # shorten for view


if __name__ == "__main__":
    encrypted_payload_hex = "2090B2EDF3B7A17F0E0D116AB70ECE5D6F2BBB247EA1202CD661F69FD4"
    app_key_hex = "00112233445566778899AABBCCDDEEFF"

    decrypted_payload = decrypt_join_accept_payload(encrypted_payload_hex, app_key_hex)

    print("🔓 Decrypted Payload (HEX):", decrypted_payload.hex().upper())

    parse_join_accept_fields(decrypted_payload)
