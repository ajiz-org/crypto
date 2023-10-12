from typing import Any, Callable, Coroutine
from utils import generate_random_nonce, hmac, make_reader, send as send1, hash
from asyncio import sleep
from math import floor, sqrt
import asyncio as s
import random


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
    read: Coroutine[Any, Any, str],
    send: Coroutine[Any, Any, None],
    title: str,
    desc: str,
    sign: Callable[[str, str], str],
):
    n = len(pwd)
    pending = n
    size = len(sign("", ""))
    await send(header(title))
    await send("Hello Guys I am the bot again")
    await send(f"Please post your names followed by {desc}")

    msgs: list[str] = list(map(lambda x: None, pwd))
    while pending > 0:
        msg = await read()
        plain, sig = msg[:-size].rstrip(), msg[-size:]
        for i in (i for i in range(n) if msgs[i] == None):
            print(sig, pwd[i], plain, sign(pwd[i], plain))
            if sig != sign(pwd[i], plain):
                continue
            pending -= 1
            if pending:
                await send(str(pending) + " to go")
            msgs[i] = plain
            break
    await send("Ok here are the names: " + ", ".join(msgs))
    return msgs


async def OTP(pwd: list[str]):
    async with make_reader() as (read, send):
        params = (pwd, read, send)
        await handle(
            *params,
            title="   ~ OTP ~    ",
            desc="the secrets you have received",
            sign=lambda key, _: key,
        )


async def HASH(pwd: list[str]):
    async with make_reader() as (read, send):
        params = (pwd, read, send)
        await handle(
            *params,
            title="  ~ HASH ~  ",
            desc="hash(Your Name:The secret)",
            sign=lambda key, plain: hash(plain + ":" + key),
        )


def getRoles(pwd: list[str]):
    size = len(pwd)
    nwolves = floor(sqrt(size))
    roles = ["Wolf"] * nwolves + ["Seer"] + ["Villager"] * (size - nwolves - 1)
    random.shuffle(roles)
    return roles


async def handleRoles(
    pwd: list[str],
    names: list[str],
    send: Coroutine[Any, Any, None],
):
    await send("Here are your roles (Wolf, Seer, Villager) as hmac(pwd, role)")
    roles = getRoles(pwd)
    for i in range(len(pwd)):
        await send(names[i] + ": " + hmac(pwd[i], roles[i]))
    return roles


async def HMAC(pwd: list[str]):
    async with make_reader() as (read, send):
        params = (pwd, read, send)
        names = await handle(
            *params,
            title="  ~ HMAC ~  ",
            desc="hmac(The secret, Your Name)",
            sign=hmac,
        )
        roles = await handleRoles(pwd, names, send)


async def NONCE(pwd: list[str]):
    async with make_reader() as (read, send):
        params = (pwd, read, send)
        nonce = generate_random_nonce()
        names = await handle(
            *params,
            title=" ~ NONCE ~ ",
            desc="nonce hmac(The secret, nonce + Your Name)",
            sign=hmac,
        )
        roles = await handleRoles(pwd, names, send)


pwd = ["af", "oa", "tt"]
# first run with no auth and note the flaw of some one else steeling the identity of some one else
# s.run(NoAuth(3))
# introduce OTP auth and proceed to role destribution, note the need to a permenant key
# s.run(OTP(pwd))
# introduce HASH
# s.run(HASH(pwd))
# and HMAC (mention KDF) and use it for role destribution
# s.run(HMAC(pwd))
# start the game by voting and show the reply attack, show the need for a nonce
s.run(NONCE(pwd))
