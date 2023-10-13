from typing import Callable
from common import compare_increment, increment_byte_array
from ..encoding import decode64, encode64
from ..hash import hmac


def get_sign_nonce(nonces: list[bytearray], sign: Callable[[str, str], str] = hmac):
    def hmac_nonce(key: str, msg: str, i: int = 0):
        nonce = nonces[i]
        increment_byte_array(nonce)
        print(nonce, key, msg)
        return sign(key, msg)

    return hmac_nonce


def get_verify_nonce(nonces: list[bytearray], sign: Callable[[str, str], str] = hmac):
    def verify_nonce(pwd: str, sig: str, plain: str, i: int = 0):
        nonce = bytearray(nonces[i])
        increment_byte_array(nonce)
        if sig != sign(pwd, plain):
            return False
        nonces[i] = nonce
        return True

    return verify_nonce
