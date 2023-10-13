from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from common import split
from .kdf import key_derivation
import os


def get_key_nonce(pwd: bytes, salt: bytes, nonce: bytearray):
    aesgcm = AESGCM(key_derivation(pwd, salt))
    min_nonce_length = 8
    padding_needed = max(0, min_nonce_length - len(nonce))
    nonce = nonce + b"\0" * padding_needed
    return aesgcm, nonce


def aes_encrypt(pwd: bytes, nonce: bytearray, plaintext: bytes):
    # Ensure that salt is unique per user/password
    salt = os.urandom(16)
    aesgcm, nonce = get_key_nonce(pwd, salt, nonce)
    ciphertext = aesgcm.encrypt(nonce, plaintext, b"")
    return salt + ciphertext


def aes_decrypt(pwd: bytes, nonce: bytearray, ciphertext: bytes):
    salt, ciphertext = split(ciphertext, 16)
    aesgcm, nonce = get_key_nonce(pwd, salt, nonce)
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, b"")
        return plaintext
    except Exception as e:
        return None
