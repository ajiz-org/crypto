from typing import overload


@overload
def split(data: str, point: int) -> tuple[str, str]:
    ...


@overload
def split(data: bytes, point: int) -> tuple[bytes, bytes]:
    ...


def split(data: str | bytes, point: int):
    a, b = data[:point], data[point:]
    if type(a) == str:
        a = a.strip()
    return a, b


def increment_byte_array(byte_array: bytearray):
    for i in range(len(byte_array)):
        byte_array[i] = (byte_array[i] + 1) & 255
        if byte_array[i] != 0:
            break


def compare_increment(new: bytes | bytearray, old: bytes | bytearray):
    int_old = int.from_bytes(old, byteorder='little')
    int_new = int.from_bytes(new, byteorder='little')
    return int_new == int_old + 1
