import hmac as hm
from hashlib import sha3_256 as sha

from .encoding import encode64

def hash(msg: str):
    return encode64(sha(msg.encode()).digest())


def hmac(key: str, msg: str):
    return encode64(hm.digest(key.encode(), msg.encode(), sha))

