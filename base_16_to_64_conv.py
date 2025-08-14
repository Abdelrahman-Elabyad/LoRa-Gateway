import base64

hex_str = "00887766554433221108070605040302011234F20B8567"
phy_bytes = bytes.fromhex(hex_str)
b64_str = base64.b64encode(phy_bytes).decode()

print(b64_str)
