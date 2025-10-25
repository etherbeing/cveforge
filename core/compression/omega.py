"""
I already surrended at this point but wtv lets try it once more that all I have left anyway :-)
1. Breaking Pigeon Hole theorem? I didnt sign for that
2. Breaking the Kolomov or wtv kalashnikov principle? I didnt sign for that
What did I sign for? nothing really but High Entropy Compressing Algorithm the heca with that xD
What should a High Entropy Compression Algorithm have?
1. (compressing high entropy payload 🥺) Nah just compressing something like 1, 2, 3, 4, 5, 6, 7, 8, 9, and so on until 255 in a 255 bytes is ok
2. Successfully failing on other payloads is also pretty cool nowadays because if not that f*cking pidgeon hole principle is going
to haunt me forever (Ik is pigeonhole).
Once said this, lets compress to our hearth contempt 😃
Nah lets notice this:
What a compression algorithm should have in consideration before shredding numbers in a very lossy way?
1. Adding all bytes is not reversable because we dont know the order of the payload for instance if we have byte 1 and 2, we can say 3
is the result of adding them but when going back (reversing) we dont know where each back were originally or even if 1 and 2 is the correct
combination.
TODOs
1. For each number in the normalization part finish the number with a 0 bit, after that 0 bit is set, we insert then the either,
succesion bit (1) or repetition bit (0). This way we are able to determine where each number ends with just one bit, for reading
we must reverse the bit array and read from last to first. Obtaining each number by using the 0 bit delimiter
"""

# import numpy as np

from math import ceil
from typing import Iterable, List, Literal, Optional, cast

from .utils.int import ilog


def bit_array_to_number(array: list[Literal[1, 0]]):
    return sum([x[1] * 2 ** (x[0]) for x in enumerate(reversed(array))])


def number_to_bit_array(number: int, length: Optional[int] = None):
    bit_array = list(map(lambda x: int(x), bin(number)[2:]))
    if length and len(bit_array) < length:
        for _ in range(len(bit_array), length):
            bit_array.insert(0, 0)
    return bit_array


# Bitalize and Unbitalize are contrary operations meaning one denies the other


def bitalize(array: list[int]):
    "Turn an set into a bit array"
    assert sorted(array) == array, "The array must be sorted"
    assert len(array) == len(set(array)), "Array must be a list of unique elements"
    return sum(map(lambda x: 2**x, array))


def unbitalize(bit_array: int):
    "Turn an bit array (in int form) into a bit array"
    remainder = bit_array
    res: list[int] = []
    while remainder > 0:
        exponent, remainder = ilog(2, remainder)
        res.append(exponent)
    return res


def normalize(array: List[int]):
    normalized_array: list[list[int]] = []
    index = 0
    while True:
        target = array[index]
        inner_array: list[int] = [target]
        normalized_array.append(inner_array)
        while True:
            index += 1
            if index == len(array):
                break
            sample: int = array[index]
            if (
                sample
                - (target + (sum(inner_array[1:]) if len(inner_array) > 1 else 0))
                == 1
            ):  # Sucession
                inner_array.append(1)
            elif target == sample:  # Repetition
                inner_array.append(0)
            else:
                index -= 1  # This is a correction for later index incremental (meaning it goes to 0)
                break
        index += 1
        if index >= len(array):
            break
    return normalized_array


def log_reduce(number: int, base: int = 100):
    remainder = number
    exponents: list[int] = []
    while remainder > 0:
        exponent, remainder = ilog(base, remainder)
        exponents.append(exponent)
    return sorted(exponents), remainder


def log_expand(array: list[int]):
    number: int = 0
    for element in array:
        number += 2**element
    return number


def higher_array(int_array: list[list[int]]):
    original_payload: list[int] = []
    TARGET_LENGTH = 8
    for element in int_array:
        original: int = element[0]
        original_payload.append(original)
        # for i in element[1]:
        #     print(i)
    return original_payload


def lower_array(array: Iterable[int]):
    """
    Apply our custom lower array that works on repetition and succession patterns (this algorithm is useful for logarithmic decomposition)
    For each array X is very likely that there is at least one repetition or sucession in the whole payload.
    For a logarithmic decomposition of base higher than 2 there is an almost always probability of repeating the payload.
    For logarithmic decomposition of base 2 there is a slight possibility of finding a succession.
    For truly random arrays (e.g. [1, 3, 2, 5]) this algorithm will fail instead the approach would be:
    log_decompose(array_to_number([1, 3, 2, 5])) = [4, 4, 3, 3, 2, 2] (Note: this values are not real just an example)
    After obtaining the log decomposition we apply this algorithm as lower_array(4, 4, 3, 3, 2, 2) this will give us something like
    [8, 6, 4] (as for repetition we add 0 which just make the last bit to duplicate itself), then if we convert the reduce the array:
    we would have something like:
    4 [4, 2, 0], and then turning that into a number would be something like 1 0 1 0 1 or what is the same 21.
    Therefore we could compress an array X into one byte.
    Compression Logic is:
    1 byte for the target from them on if
    """
    normalized_parts = normalize(cast(List[int], array))
    lowered_array: list[list[int | None]] = []
    for part in normalized_parts:
        parts = part[1:]
        lowered_array.append(
            [
                part[0],
                (
                    bit_array_to_number(cast(list[Literal[1, 0]], parts))
                    if parts
                    else None
                ),
            ]
        )
    return lowered_array


def compress(
    value: bytes,
):  # I wish this shit actually works xD may God change the rules of the universe for this to work 🙏
    # Ideal Case
    # p = [x for x in range(256)]
    # print(f"@-> From {p} {sum([l.bit_length() for l in p])/8} bytes")
    # cp = lower_array(p)
    # print(f"@-> To {cp} {sum([p.bit_length() for p in cp])/8} bytes")
    # End of ideal case
    print(f"@-> {value} {len(value)} bytes")
    cp = lower_array(value)
    assert higher_array(cp) == value, "Reverse operation is invalid at step #1"
    print(cp)
