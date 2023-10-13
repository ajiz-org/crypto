import aiohttp
from aiohttp_sse_client.client import EventSource
from contextlib import asynccontextmanager
import json
import os
import hmac as hm
from hashlib import sha3_256 as sha
from base64 import b64encode, b64decode

def encode64(b: bytearray | bytes):
    return b64encode(b).decode()

def decode64(b64: str):
    return b64decode(b64)

def hash(msg: str):
    return encode64(sha(msg.encode()).digest())


def hmac(key: str, msg: str):
    return encode64(hm.digest(key.encode(), msg.encode(), sha))

def get_hmac_nonce(nonce_bytes: bytes):
    nonce = bytearray(nonce_bytes)
    def hmac_nonce(key: str, msg: str):
        increment_byte_array(nonce)
        return encode64(nonce)+hmac(key, encode64(nonce)+msg)
    return hmac_nonce

def get_verify_nonce(nonces: list[bytes], sign = hmac):
    def verify_nonce(pwd: str, sig: str, plain: str, i = 0):
        nonce_size = len(encode64(nonces[0]))
        nonce_encoded, sig = sig[:nonce_size], sig[nonce_size:]
        nonce = decode64(nonce_encoded)
        if nonce != nonces[i] + 1 or sig != sign(pwd, nonce_encoded + plain):
            return False
        nonces[i] = nonce
        return True
    return verify_nonce


async def send(msg: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://rest.ably.io/channels/channel1/messages",
            json={"name": "msg", "data": msg},
            headers={
                "Content-Type": "application/json",
                "Authorization": "Basic cVJYUXBBLllrT1h0dzpmVHhzN3NpSjVJMTMxRTFrcnBQZHBaaURmMFZ4MkhyeDN4eF9EMWNxeXhr",
            },
        ) as response:
            return await response.json()


url = (
    "https://realtime.ably.io/sse?"
    "v=1.2&channels=channel1&key=qRXQpA.YkOXtw:fTxs7siJ5I131E1krpPdpZiDf0Vx2Hrx3xx_D1cqyxk"
)


@asynccontextmanager
async def make_reader():
    pending: set[str] = set()
    async with EventSource(url) as client:
        async def write(msg: str):
            res = await send(msg)
            pending.add(res['messageId'])

        async def read() -> str:
            while True:
                ev = await anext(client)
                data = json.loads(ev.data)
                id = data['id'][:-2]
                if id in pending:
                    pending.remove(id)
                else:
                    return data['data']

        yield (read, write)

def increment_byte_array(byte_array):
    for i in range(len(byte_array)):
        byte_array[i] = (byte_array[i] + 1) & 255
        if byte_array[i] != 0:
            break

def generate_random_nonce():
    return os.urandom(6)


def generateRSA() -> tuple[str, str]:
    return ""


def obfuscate(doc: str, sign_key: str) -> str:
    return ""
