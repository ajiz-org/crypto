from typing import Coroutine


def send(msg: str):
    pass

def make_reader():
    async def read() -> str:
        return ""
    return read


def generateRSA() -> tuple[str, str]:
    return ""


def hmac(secret: str, content: str) -> str:
    return ""


def prepare_blind(doc: str, sign_key: str, )