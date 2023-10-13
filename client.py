import aiohttp
from aiohttp_sse_client.client import EventSource
from contextlib import asynccontextmanager
import json

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

