from typing import Callable
from common import compare_increment, increment_byte_array
from ..encoding import decode64, encode64
from ..hash import hmac


def get_hmac_nonce(nonce: bytearray):
    def hmac_nonce(key: str, msg: str):
        increment_byte_array(nonce)
        return encode64(nonce) + hmac(key, encode64(nonce) + msg)

    return hmac_nonce


def get_verify_nonce(nonces: list[bytearray], sign=hmac):
    def verify_nonce(pwd: str, sig: str, plain: str, i=0):
        nonce_size = len(encode64(nonces[0]))
        nonce_encoded, sig = sig[:nonce_size], sig[nonce_size:]
        nonce = decode64(nonce_encoded)
        if not compare_increment(nonce, nonces[i]) or sig != sign(
            pwd, nonce_encoded + plain
        ):
            return False
        increment_byte_array(nonces[i])
        return True

    return verify_nonce
