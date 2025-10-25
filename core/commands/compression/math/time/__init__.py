from math import log
from time import time


def get_simple_seed(number: int):
    count = 0
    start = time()
    while count < number:
        count += 1
    end = time()
    return end - start


def get_fast_seed(number: int, exponent: float = 1.5):
    count = 0
    value = 2
    start = time()
    while value < number:
        temp = value**exponent
        if temp <= number:
            value = temp
            count += 1
        else:
            break
    end = time()
    return (end - start), count, value


def complete_spot(
    number_distance: int,
    velocity_base: int = 3,
    mod: int = 2 ** (8 * 4),
):
    """
    :param distance: The number or distance to compress
    :param mod: The mod parameter to store in 4 bytes helps to hurry the number resolution when decompressing.
    """
    BT_BASE = 2
    bt = number_distance.bit_length()
    velocity = velocity_base**bt
    t = round(
        velocity / number_distance
    )  # time estimated for going through the whole number (treating the number as space)
    mod_part = number_distance % mod  # it fits 4 bytes
    tx = BT_BASE  # round(number_distance - mod_part)/mod # we need now to identify a combination such that x=x1**e.
    e = round(log(tx, (number_distance - mod_part) / mod))
    # test reversability
    base_x = round((BT_BASE ** (bt - 1) - mod_part) / mod)
    top_x = round((BT_BASE ** (bt) - mod_part) / mod)
    x = base_x
    while x < top_x:
        temp_d = mod * x + mod_part
        assert (
            temp_d % mod == mod_part
        ), f"Something is wrong {temp_d%mod} is not {mod_part}"
        # if temp_d > number_distance:
        #     print('we did go to far')
        # elif temp_d < BT_BASE**(bt-1):
        #     print("we are too little")
        if temp_d == number_distance:
            print("decompressed?")
            break
        print(f"{x} {temp_d}%{mod} == {temp_d%mod} {temp_d%mod==mod_part}")
        x += 1
    return t, mod_part, bt, base_x, top_x, e
