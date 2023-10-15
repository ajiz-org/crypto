from typing import Any, Callable, Coroutine, Literal
from client import make_reader, send as send1
from common import split
from utils import make_nonces, hmac, hash, encode64, make_key
from asyncio import sleep
from math import floor, sqrt
import re
import random
from collections import Counter


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
    gen_pwd: list[str],
    pwd: list[str],
    read: Coroutine[Any, Any, str],
    send: Coroutine[Any, Any, None],
    title: str,
    desc: str,
    size: int,
    verify: Callable[[str, str, str, int], bool],
):
    n = len(gen_pwd)
    pending = len(pwd)
    j = 0
    await send(header(title))
    await send("Hello Guys I am the bot again")
    await send(f"Please post your names followed by {desc}")

    names: list[str] = list(pwd)
    while pending > 0:
        msg = await read()
        plain, sig = split(msg, -size)
        print("plain=", plain, "sig=", sig)
        print(n, gen_pwd)
        for i in (i for i in range(n)):
            if gen_pwd[i] == None:
                continue
            if not verify(gen_pwd[i], sig, plain, j):
                continue
            if plain in names:
                await send("bot: " + plain + " is used")
                continue
            pending -= 1
            if pending:
                await send("bot: " + str(pending) + " to go")
            names[j] = plain
            pwd[j] = gen_pwd[i]
            gen_pwd[i] = None
            j += 1
            break
        else:
            print("strange")
    await send("bot: Ok here are the names: " + ", ".join(names))
    return names


async def handle_names_with_sign(
    pwd_gen: list[str],
    pwd: list[str],
    read: Coroutine[Any, Any, str],
    send: Coroutine[Any, Any, None],
    title: str,
    desc: str,
    sign: Callable[[str, str], str],
):
    size = len(sign(pwd_gen[0], pwd_gen[0]))
    params = (pwd_gen, pwd, read, send, title, desc, size)
    return await handle_names(
        *params,
        lambda pwd, sig, plain, _: sig == sign(pwd, plain),
    )


async def OTP(gen_pwd: list[str], pwd: list[str]):
    async with make_reader() as (read, send):
        params = (gen_pwd, pwd, read, send)
        await handle_names_with_sign(
            *params,
            title="   ~ OTP ~    ",
            desc="the secrets you have received",
            sign=lambda key, _: key,
        )


async def HASH(gen_pwd: list[str], pwd: list[str]):
    async with make_reader() as (read, send):
        params = (gen_pwd, pwd, read, send)
        await handle_names_with_sign(
            *params,
            title="  ~ HASH ~  ",
            desc="hash(Your Name:The secret)",
            sign=lambda key, plain: hash(plain + ":" + key),
        )


def get_roles(pwd: list[str]) -> list[Literal["Wolf", "Seer", "Villager"]]:
    size = len(pwd)
    nwolves = floor(sqrt(size))
    roles = ["Wolf"] * nwolves + ["Seer"] + ["Villager"] * (size - nwolves - 1)
    random.shuffle(roles)
    return roles


async def handle_roles(
    pwd: list[str],
    names: list[str],
    send: Coroutine[Any, Any, None],
    sign: Callable[[str, str, int], str],
):
    await send("bot: Here are your roles (Wolf, Seer, Villager) as hmac(pwd, role)")
    roles = get_roles(pwd)
    for i in range(len(pwd)):
        await send(names[i] + ": " + sign(pwd[i], roles[i], i))
    return roles


async def HMAC(gen_pwd: list[str], pwd: list[str]):
    async with make_reader() as (read, send):
        params = (gen_pwd, pwd, read, send)
        names = await handle_names_with_sign(
            *params,
            title="  ~ HMAC ~  ",
            desc="hmac(The secret, Your Name)",
            sign=hmac,
        )
        await handle_roles(pwd, names, send, lambda *x: hmac(*x[:-1]))


async def play_game(
    verify: Callable[[str, str, str, int], bool],
    sign: Callable[[str, str, int], str],
    encrypt: Callable[[str, str, int], str],
    decrypt: Callable[[str, str, int], str | None],
    names: list[str],
    roles: list[Literal["Wolf", "Seer", "Villager"]],
    pwd: list[str],
    read: Coroutine[Any, Any, str],
    send: Coroutine[Any, Any, None],
):
    n = len(pwd)
    remaining = n
    while True:
        wolves = [i for i in range(len(roles)) if roles[i] == "Wolf"]
        n_wolves = len(wolves)
        if n_wolves == 0:
            return "Villagers"
        if n_wolves == remaining:
            return "Wolves"
        # Until night, collect villagers votes
        wolves_votes = dict[int, int]()
        villagers_votes = dict[int, int]()
        messages: list[str] = []
        while len(villagers_votes) != remaining:
            msg: str = await read()
            i = next(
                (
                    i
                    for i in range(len(names))
                    if names[i]
                    if msg.startswith(names[i] + ":")
                ),
                None,
            )
            if i == None:
                print("not a villager vote", msg)
                messages.append(msg)
                continue

            sig_size = len(hmac("", ""))
            m = re.match("^(.*?:\s*ban\s+(.*?))\s+(.{" + str(sig_size) + "})$", msg)
            if not m:
                print(msg, "incorrect format")
                continue
            if not verify(pwd[i], m[3], m[2], i):
                print("incorrect signature")
                continue
            if m[2] not in names:
                continue
            await send("bot: " + m[1])
            banned = m[2]
            j = names.index(banned)
            villagers_votes[i] = j
        value_counts = Counter(villagers_votes.values())
        maxc = max(value_counts.values())
        winners = [value for value, count in value_counts.items() if count == maxc]
        if len(winners) == 1:
            (i,) = winners
            name = names[i]
            role = roles[i]
            if role == "Seer":
                await send("bot: seriously ? you have banned the seer, well good luck!")
            elif role == "Villager":
                await send("bot: shame, you have banned an alley")
            else:
                await send("bot: good, you have banned a wolf")
                n_wolves -= 1
                wolves.remove(i)
            roles[i] = None
            pwd[i] = None
            names[i] = None
            remaining -= 1
            await send(
                f"bot: {name} banned\n"
                + "\n".join(
                    f"{names[k]} ({sign(pwd[k], name, k)})" for k in range(n) if pwd[k]
                )
            )
            if n_wolves == 0:
                continue
        else:
            await send("bot: shame, you couldn't reach a concensus")

        async def handle_seer(msg: str):
            i = roles.index("Seer")
            plain = decrypt(pwd[i], msg, i)
            if plain is None:
                return False
            if not plain.startswith("see "):
                return False
            player = plain[4:].strip()
            if player not in names:
                return False
            j = names.index(player)
            await send(encrypt(pwd[i], roles[j], i))
            return True

        def handle_wolves(msg: str):
            for i in wolves:
                plain = decrypt(pwd[i], msg, i)
                if plain is None:
                    continue
                if not plain.startswith("eat "):
                    return
                player = plain[4:].strip()
                if player not in names:
                    return
                wolves_votes[i] = names.index(player)
                return

        if "Seer" in roles:
            await send("bot: it's night, everyone goes asleep besides the seer")
            for msg in messages:
                if await handle_seer(msg):
                    break
            else:
                while not await handle_seer(await read()):
                    pass
            await send("bot: the seer sleeps, wolves wake up")
        else:
            await send("bot: it's night, everyone goes asleep besides the wolves")
        for msg in messages:
            handle_wolves(msg)
        while len(wolves_votes) != n_wolves:
            handle_wolves(await read())

        print("wolves_votes=", wolves_votes)
        value_counts = Counter(wolves_votes.values())
        maxc = max(value_counts.values())
        winners = [value for value, count in value_counts.items() if count == maxc]
        await send("bot: Its morning, everyone wakes up")
        if len(winners) == 1:
            (i,) = winners
            roles[i] = None
            pwd[i] = None
            names[i] = None
            await send(
                f"bot: {name} eaten\n"
                + "\n".join(
                    f"{names[k]} ({sign(pwd[k], name, k)})" for k in range(n) if pwd[k]
                )
            )
            remaining -= 1
        else:
            await send(
                "bot: the wolves couldn't reach a consensus, and no villager has been eaten"
            )


async def NONCE(gen_pwd: list[str], pwd: list[str]):
    async with make_reader() as (read, send):
        params = (gen_pwd, pwd, read, send)
        (nonce, verify, sign, encrypt, decrypt, _) = make_nonces(len(pwd))
        names = await handle_names(
            *params,
            title=" ~ NONCE ~ ",
            desc="hmac(The secret, nonce_encoded + Your Name)\n"
            "nonce_encoded=encode64(nonce_encoded)\n"
            f"starting nonce encoded = {encode64(nonce)}",
            size=len(hmac("", "")),
            verify=verify,
        )
        roles = await handle_roles(pwd, names, send, sign)
        await send(
            "bot: Ok now here is the shared key you wolves can use to talk securely"
        )
        wolves = [i for i in range(len(roles)) if roles[i] == "Wolf"]
        secret = make_key()
        for i in wolves:
            await send(encrypt(pwd[i], secret, i))
        await send(
            "bot: once you agree on the villager to eat, send me his name\n"
            "enc('eat ' +  your_target)"
        )
        await send(
            "bot: at the same time, the villagers agree on someone and vote to exclude him\n"
            "your_name + ': ban ' +  your_target + sign(your_target)"
        )
        winner = await play_game(
            verify, sign, encrypt, decrypt, names, roles, pwd, read, send
        )
        await send('bot: ' + winner + ' won')


