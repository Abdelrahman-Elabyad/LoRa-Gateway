#need to genrate NEWSKEY AND APPSKEY
#Need to sotre them in teh device yaml file so they can be extracted accordign to teh deviec ADdress
def derive_session_keys(key_type: int, app_key: bytes, app_nonce: bytes, net_id: bytes, dev_nonce: bytes) -> bytes:
    ...
