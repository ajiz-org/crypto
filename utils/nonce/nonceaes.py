from typing import Callable
from common import increment_byte_array
from cryplib import aes_encrypt, aes_decrypt
from ..encoding import decode64, encode64


def get_nonce_decrypt(
    nonces: list[bytes],
    decrypt: Callable[[bytes, bytearray, bytes], bytes | None] = aes_decrypt,
):
    def nonce_decrypt(pwd: str, cipher: str, i=0):
        try:
            nonce = bytearray(nonces[i])
            increment_byte_array(nonce)
            plain = decrypt(pwd.encode(), nonce, decode64(cipher))
            nonces[i] = nonce
            return plain.decode()
        except Exception as e:
            print(e)
            return None
    return nonce_decrypt


def get_nonce_encrypt(
    nonces: list[bytes],
    encrypt: Callable[[bytes, bytearray, bytes], bytes] = aes_encrypt,
):
    def nonce_encrypt(pwd: str, plain: str, i=0):
        nonce = nonces[i]
        increment_byte_array(nonce)
        cipher = encrypt(pwd.encode(), nonce, plain.encode())
        nonces[i] = nonce
        return encode64(cipher)
    return nonce_encrypt
