from typing import Callable
from ..encoding import encode64
from .noncesign import generate_random_nonce, get_hmac_nonce, get_verify_nonce
import os


def generate_random_nonce():
    return os.urandom(6)


def make_nonces(size: int, sign: Callable[[str, str], str]):
    nonce = generate_random_nonce()
    nonces = [bytearray(nonce) for i in range(size)]
    nonce_size = len(encode64(nonce))

    return (
        (nonce, nonce_size, nonces),
        get_verify_nonce(nonces, sign),
        get_hmac_nonce(nonces[-1]),
    )
