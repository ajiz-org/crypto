from typing import Any, Callable, Coroutine, Tuple
from utils import hmac, make_reader, send as send1, hash
from asyncio import sleep
import asyncio as s


def header(s: str):
    return (
        "--------------------------------\n"
        "-------- GAME START --------\n"
        f"-------- {s} --------\n"
        "--------------------------------"
    )


async def NoAuth(n: int):
    async with make_reader() as (read, send):
        await send(header("~ No Auth ~"))
        await send("Hello Guys I am the bot that's gonna make you go through this game")
        await send("Please post your names")
        await sleep(1)
        await send1("Salah")
        msgs: list[str] = [await read() for _ in range(n)]
        await send("Ok here are the names: " + ", ".join(msgs))


async def handle(
    pwd: list[str],
    title: str,
    read: Coroutine[Any, Any, str],
    send: Coroutine[Any, Any, None],
    sign: Callable[[str, str], str],
):
    n = len(pwd)
    pending = n
    size = len(sign('', ''))
    await send(header(title))
    await send("Hello Guys I am the bot again")
    await send("Please post your names followed by the secrets you have received")

    msgs: list[str] = list(map(lambda x: None, pwd))
    while pending > 0:
        msg = await read()
        plain, sig = msg[:-size].rstrip(), msg[-size:]
        for i in (i for i in range(n) if msgs[i] == None):
            if sig != sign(pwd[i], plain):
                continue
            pending -= 1
            if pending:
                await send(str(pending) + " to go")
            msgs[i] = plain
            break
    await send("Ok here are the names: " + ", ".join(msgs))


async def OTP(pwd: list[str]):
    async with make_reader() as (read, send):
        await send(header())
        await send("Hello Guys I am the bot again")
        await send("Please post your names followed by the secrets you have received")

        msgs: list[str] = list(map(lambda x: None, pwd))
        while pending > 0:
            msg = await read()
            for i in (i for i in range(n) if msgs[i] == None if msg.endswith(pwd[i])):
                pending -= 1
                await send(str(pending) + " to go")
                msgs[i] = (msg[: -len(pwd[i])]).rstrip()
                break
        await send("Ok here are the names: " + ", ".join(msgs))


async def HASH(pwd: list[str]):
    n = len(pwd)
    pending = n
    size = len(hash(""))
    async with make_reader() as (read, send):
        await send(header("  ~ HASH ~  "))
        await send("Hello Guys I am the bot again")
        await send("Please post your names followed by the secrets you have received")

        msgs: list[str] = list(map(lambda x: None, pwd))
        while pending > 0:
            msg = await read()
            plain, sign = msg[:-size].rstrip(), msg[-size:]
            for i in (i for i in range(n) if msgs[i] == None):
                if sign != hash(plain + ":" + pwd[i]):
                    continue
                pending -= 1
                if pending:
                    await send(str(pending) + " to go")
                msgs[i] = plain
                break
        await send("Ok here are the names: " + ", ".join(msgs))


async def HMAC(pwd: list[str]):
    n = len(pwd)
    pending = n
    size = len(hmac("", ""))
    async with make_reader() as (read, send):
        await send(header("  ~ HMAC ~  "))
        await send("Hello Guys I am the bot again")
        await send("Please post your names followed by the secrets you have received")

        msgs: list[str] = list(map(lambda x: None, pwd))
        while pending > 0:
            msg = await read()
            plain, sign = msg[:-size].rstrip(), msg[-size:]
            for i in (i for i in range(n) if msgs[i] == None):
                if sign != hmac(pwd[i], plain):
                    continue
                pending -= 1
                if pending:
                    await send(str(pending) + " to go")
                msgs[i] = plain
                break
        await send("Ok here are the names: " + ", ".join(msgs))


# s.run(NoAuth(3))
# s.run(OTP(["af", "oa", "tt"]))
s.run(HMAC(["af", "oa", "tt"]))
