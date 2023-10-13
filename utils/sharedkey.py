import os
from .encoding import encode64


def make_key():
    return encode64(os.urandom(6))
