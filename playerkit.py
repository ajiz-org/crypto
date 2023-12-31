from typing import Callable
from cryplib.aes import aes_decrypt, aes_encrypt
from utils.encoding import decode64, encode64
from utils import make_nonces, hmac


def get_role(sig, verif: Callable[[str, str], bool]):
    for role in ("Wolf", "Seer", "Villager"):
        if verif(sig, role):
            return role


def use_nonce(nonce_encoded: str):
    return make_nonces(1, hmac, decode64(nonce_encoded))


def mykit(nonce_encoded: str, pwd: str):
    history: list[str] = []
    nonce, verif, sign, enc, dec, undo = use_nonce(nonce_encoded)

    def myhistory():
        return history

    def myverif(sig: str, plain: str):
        ok = verif(pwd, sig, plain)
        if ok:
            history.append(f"verif('{sig}', '{plain}')")
        return ok

    def mysign(plain: str):
        history.append(f"sign('{plain}')")
        return sign(pwd, plain)

    def bot_enc(plain: str):
        history.append(f"enc('{plain}')")
        return enc(pwd, plain)

    def bot_dec(cipher: str):
        secret_encoded = dec(pwd, cipher)
        if secret_encoded is None:
            return None
        history.append(f"dec('{cipher}')")
        key = decode64(secret_encoded)

        def encrypt(plain: str):
            return encode64(aes_encrypt(key, None, plain.encode()))

        def decrypt(cipher: str):
            return aes_decrypt(key, None, decode64(cipher)).decode()

        return (encrypt, decrypt)

    def get_secret(*cipher: list[str]):
        return next(i for i in (bot_dec(x) for x in cipher) if i)

    def myundo():
        undo()
        return history.pop()

    def myrole(sig: str):
        return get_role(sig, myverif)

    return (nonce, myverif, mysign, bot_enc, get_secret, myrole, myundo, myhistory)
