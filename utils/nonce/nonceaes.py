from typing import Callable
from cryplib import aes_encrypt, aes_decrypt


def get_nonce_decrypt(
    nonces: list[bytes],
    decrypt: Callable[[bytes, bytes, bytes], bytes | None] = aes_decrypt,
):
    def nonce_decrypt(pwd: str, cipher: str, i=0):
        nonce = nonces[i] + 1
        plain = decrypt(pwd, nonce, cipher)
        if plain is None:
            return
        nonces[i] = nonce
        return plain.decode()
    return nonce_decrypt


def get_nonce_encrypt(
    nonces: list[bytes],
    encrypt: Callable[[bytes, bytes, bytes], bytes] = aes_encrypt,
):
    def nonce_encrypt(pwd: str, plain: str, i=0):
        nonce = nonces[i] + 1
        cipher = encrypt(pwd, nonce, plain)
        nonces[i] = nonce
        return cipher
    return nonce_encrypt
