from utils.encoding import decode64
from utils import make_nonces, hmac

def use_nonce(nonce_encoded: str):
    return make_nonces(1, hmac, decode64(nonce_encoded))
