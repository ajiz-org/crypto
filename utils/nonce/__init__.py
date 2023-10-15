from typing import Callable

from ..hash import hmac
from ..encoding import encode64
from .noncesign import get_sign_nonce, get_verify_nonce
from .nonceaes import get_nonce_decrypt, get_nonce_encrypt
import os


def generate_random_nonce():
    return os.urandom(6)


def make_nonces(size: int, sign=hmac, nonce=generate_random_nonce()):
    nonces = [bytearray(nonce) for _ in range(size)]

    def undo():
        nonces[0] = bytearray(
            (int.from_bytes(nonces[0], byteorder="little") - 1).to_bytes(
                len(nonces[0]), byteorder="little"
            )
        )

    return (
        nonce,
        get_verify_nonce(nonces, sign),
        get_sign_nonce(nonces, sign),
        get_nonce_encrypt(nonces),
        get_nonce_decrypt(nonces),
        undo,
    )
