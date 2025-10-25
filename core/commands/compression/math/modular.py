from math import ceil, log
from time import time


def mod_normalize(number: int, base: int = 2):
    mod = 256
    # 1. The number is between: 2**bit_length and 2**(bit_length-1)
    mod_part = number % mod
    # 2. The number can be reached from 2**(bit_length-1) by exploring all of the values of m*x+n therefore
    bottom_x = ceil((base ** (number.bit_length() - 1) - mod_part) / mod)
    up_x = ceil((base ** number.bit_length() - mod_part) / mod)
    x = bottom_x
    count = 0
    start = time()
    while (
        True
    ):  # TODO If we can represent this mathematically we successfully compressed high entropy payload (This is a BIG IF)
        y = mod * x + mod_part
        if y > number:  # this means the x is too large
            up_x = x
        elif y < number:  # means its too small
            bottom_x = x
        else:  # means is the expected x
            break
        x = (up_x + bottom_x) // 2
        count += 1
        # if y == number:
        #     break
        # elif y > number:
        #     raise ValueError("We couldn't revert this to figure it out the time param")
    end = time()
    taken_time = end - start
    return mod_part, ceil(taken_time), taken_time, number.bit_length(), count


def mod(number: int, base: int = 2, mod: int = 256):
    log_part = log(number, base)
    mod_part = number % mod
    x = (number - mod_part) / mod
    return log_part, mod_part, x


def unmod(log_part: float, mod_part: int, x: float, base: int = 2, mod: int = 256):
    start = mod * x + mod_part
    end = base**log_part
    range_mod = end - start
    return start, end, range_mod, range_mod / mod_part
