import asyncio
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
    timeout = aiohttp.ClientTimeout(sock_read=0)
    session: aiohttp.ClientSession = None
    client: EventSource = None
    task: asyncio.Task = None
    try:
        session = aiohttp.ClientSession(timeout=timeout)
        client = EventSource(url, session=session)
        task = asyncio.create_task(client.connect(retry=1000))
    except:
        pass
    try:
        async def write(msg: str):
            while True:
                try:
                    res = await send(msg)
                    break
                except:
                    pass
            pending.add(res['messageId'])

        async def read() -> str:
            nonlocal client, session, task
            while True:
                try:
                    await task
                    ev = await anext(client)
                    data = json.loads(ev.data)
                    id = data['id'][:-2]
                    if id in pending:
                        pending.remove(id)
                    else:
                        return data['data']
                except Exception as e:                    
                    if client:
                        await client.close()
                        await session.close()
                    session = aiohttp.ClientSession(timeout=timeout)
                    client = EventSource(url, session=session)
                    task = asyncio.create_task(client.connect(retry=1000))
                    print('error timeout', e)
        yield (read, write)
    finally:
        if client:
            await client.close()
            await session.close()

