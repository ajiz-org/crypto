from typing import Any, Callable, Coroutine
from utils import (
    decode64,
    encode64,
    generate_random_nonce,
    get_hmac_nonce,
    get_verify_nonce,
    hmac,
    increment_byte_array,
    make_reader,
    send as send1,
    hash,
)
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


async def handle_names(
    pwd: list[str],
    read: Coroutine[Any, Any, str],
    send: Coroutine[Any, Any, None],
    title: str,
    desc: str,
    size: int,
    verify: Callable[[str, str, str, int], bool],
):
    n = len(pwd)
    pending = n
    await send(header(title))
    await send("Hello Guys I am the bot again")
    await send(f"Please post your names followed by {desc}")

    names: list[str] = list(map(lambda x: None, pwd))
    while pending > 0:
        msg = await read()
        plain, sig = msg[:-size].rstrip(), msg[-size:]
        plain = plain.rstrip()
        for i in (i for i in range(n) if names[i] == None):
            if not verify(pwd[i], sig, plain, i):
                continue
            pending -= 1
            if pending:
                await send(str(pending) + " to go")
            names[i] = plain
            break
    await send("Ok here are the names: " + ", ".join(names))
    return names


async def handle_names_with_sign(
    pwd: list[str],
    read: Coroutine[Any, Any, str],
    send: Coroutine[Any, Any, None],
    title: str,
    desc: str,
    sign: Callable[[str, str], str],
):
    size = len(sign("", ""))
    params = (pwd, read, send, title, desc, size)
    return await handle_names(
        *params,
        lambda pwd, sig, plain, _: sig == sign(pwd, plain),
    )


def make_nonces(size: int, sign: Callable[[str, str], str]):
    nonce = generate_random_nonce()
    nonces = [nonce] * size
    nonce_size = len(encode64(nonce))

    return (
        (nonce, nonce_size, nonces),
        get_verify_nonce(nonces, sign),
        get_hmac_nonce(nonces[-1]),
    )


async def OTP(pwd: list[str]):
    async with make_reader() as (read, send):
        params = (pwd, read, send)
        await handle_names_with_sign(
            *params,
            title="   ~ OTP ~    ",
            desc="the secrets you have received",
            sign=lambda key, _: key,
        )


async def HASH(pwd: list[str]):
    async with make_reader() as (read, send):
        params = (pwd, read, send)
        await handle_names_with_sign(
            *params,
            title="  ~ HASH ~  ",
            desc="hash(Your Name:The secret)",
            sign=lambda key, plain: hash(plain + ":" + key),
        )


def get_roles(pwd: list[str]):
    size = len(pwd)
    nwolves = floor(sqrt(size))
    roles = ["Wolf"] * nwolves + ["Seer"] + ["Villager"] * (size - nwolves - 1)
    random.shuffle(roles)
    return roles


async def handle_roles(
    pwd: list[str],
    names: list[str],
    send: Coroutine[Any, Any, None],
    sign: Callable[[str, str], str],
):
    await send("Here are your roles (Wolf, Seer, Villager) as hmac(pwd, role)")
    roles = get_roles(pwd)
    for i in range(len(pwd)):
        await send(names[i] + ": " + sign(pwd[i], roles[i]))
    return roles


async def HMAC(pwd: list[str]):
    async with make_reader() as (read, send):
        params = (pwd, read, send)
        names = await handle_names_with_sign(
            *params,
            title="  ~ HMAC ~  ",
            desc="hmac(The secret, Your Name)",
            sign=hmac,
        )
        roles = await handle_roles(pwd, names, send, hmac)


async def NONCE(pwd: list[str]):
    async with make_reader() as (read, send):
        params = (pwd, read, send)
        ((nonce, nonce_size), verify, sign) = make_nonces(len(pwd) + 1, hmac)

        names = await handle_names(
            *params,
            title=" ~ NONCE ~ ",
            desc="nonce_encoded + hmac(The secret, nonce_encoded + Your Name)\n"
            "nonce_encoded=encode64(nonce_encoded)\n"
            f"starting nonce encoded = ${encode64(nonce)}",
            size=nonce_size + len(hmac("", "")),
            verify=verify,
        )
        roles = await handle_roles(pwd, names, send, sign)
        send('Ok now here is the shared key')


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
# mention salt, kdf and modular crypt format
s.run(NONCE(pwd))
# talk about AES, block cipher mode, padding
