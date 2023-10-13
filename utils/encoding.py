from base64 import b64encode, b64decode

def encode64(b: bytearray | bytes):
    return b64encode(b).decode()

def decode64(b64: str):
    return b64decode(b64)

