import aiohttp
from requests import post
from aiohttp_sse_client.client import EventSource
from contextlib import asynccontextmanager
import json
import os
import hmac as hm
from hashlib import sha3_256 as sha
from base64 import b64encode as e

def hash(msg: str):
    return e(sha(msg.encode()).digest()).decode()


def hmac(key: str, msg: str):
    return e(hm.digest(key.encode(), msg.encode(), sha)).decode()


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
    return bytearray(os.urandom(4))


def generateRSA() -> tuple[str, str]:
    return ""


def obfuscate(doc: str, sign_key: str) -> str:
    return ""
