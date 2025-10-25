from math import ceil


def get_remainder(x: int, size: int = 2**32):
    return x % size


def get_bit_length(x: int):
    return x.bit_length()


def get_exponent_range(x: int):
    bit_length = get_bit_length(x)
    return [bit_length - 1, bit_length]


def get_range(x: int, base: int = 2):
    bases = get_exponent_range(x)
    return base ** bases[0], base ** bases[1]


def get_posibilities(top_exp: int, mod: int, base: int = 2) -> int:
    n_range: int = base**top_exp - base ** (top_exp - 1)
    n_range = ceil(n_range / mod)
    return n_range


def get_significance(
    top_exp: int, remainder: int, orignal_x: int, base: int = 2, shrink_size: int = 32
):
    # remainder is a regulator
    # top_exp is the storage
    significance = orignal_x / base**top_exp
    print(round(significance * base**top_exp))
    modular_correction = (orignal_x - remainder) / base**shrink_size
    return significance, modular_correction


def modular_reduction(x: int):
    parts: list[int] = []
    remainders: list[int] = []
    exponent: int = x.bit_length() // 2
    base: int = 2
    value = x
    while value > 0:
        value, r = divmod(value, base**exponent)
        remainders.append(r)
        parts.append(value)
    return parts, remainders
