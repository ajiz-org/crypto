from typing import Callable
from common import compare_increment, increment_byte_array
from ..encoding import decode64, encode64
from ..hash import hmac


def get_sign_nonce(nonces: list[bytearray], sign: Callable[[str, str], str] = hmac):
    def sign_nonce(key: str, msg: str, i: int = 0):
        nonce = nonces[i]
        increment_byte_array(nonce)
        print(nonce, key, msg)
        return sign(key, encode64(nonce) + msg)

    return sign_nonce


def get_verify_nonce(nonces: list[bytearray], sign: Callable[[str, str], str] = hmac):
    def verify_nonce(pwd: str, sig: str, plain: str, i: int = 0):
        nonce = bytearray(nonces[i])
        increment_byte_array(nonce)
        print(
            "verifying sig=",
            sig,
            "pwd=",
            pwd,
            "nonce=",
            nonce,
            "plain=",
            plain,
            "against=",
            sign(pwd, encode64(nonce) + plain),
        )
        if sig != sign(pwd, encode64(nonce) + plain):
            return False
        nonces[i] = nonce
        return True

    return verify_nonce
