from utils import generateRSA, make_reader, hmac, send

class CA:
    pub: str
    def verif(str: str) -> str | None:
        pass

class DSA:
    def sign(str: str) -> str:
        pass
    def verif(str: str) -> str | None:
        pass

async def PlayerThread(pwd: str, ca: CA, nplayer: int):
    read = make_reader()

    [id, id_key] = generateRSA()
    # send the proof
    send(hmac(id, pwd) + ' ' + id)
    # wait for all signatures to be ready
    players: set[str] = set()
    while len(players) < nplayer:
        v = ca.verif(await read())
        # when v is irrelevent
        if not v: continue
        players.add(v)
    # generate secret identities
    [hid, hid_key] = generateRSA()
    # blind signature
    [obf_doc, token] = obfuscate(hid, ca.pub)
    send(obf_doc)
    # wait for hidden identity to be signed
    while len(players) < nplayer:
        v = ca.verif(await read())
        # when v is irrelevent
        if not v: continue
        players.add(v)
        
