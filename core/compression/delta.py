"""
After some days perhaps weeks of writing this file lets see what we got:
1. log decomposition is useful for entropy downgrading, it give us the possibility of turning a seemingly random array of bytes into
an structured behaviour. (descending order).
2. delta encoding give us the possibility of reducing the size of the log array but destroy the structure and make it then harder to encode.
3. CRT is good to encode together some numbers allowing us to decode from one number multiple numbers.
4. Shanon Score give us the randomness of a payload but as we can see a log decomposition is not so random but shanon say it is, therefore
Shanon Score/Theorem give us the importance of a number in a payload, which is different from entropy and what else.
5. If we use the Shanon Score in the delta decomposition we got whether or not a succesive pattern can be found in the array.

"""

from collections import Counter
from math import log
from random import randbytes
from typing import Any, Literal, Optional, cast

from sympy import nextprime  # type: ignore
from sympy.ntheory.modular import crt  # type: ignore

from core.compression.utils.int import ilog


# Encoding functions
def delta_encoding(array: list[int]):
    delta_encoded: list[int] = [array[0]]
    index = 1
    while index < len(array):
        delta_encoded.append(array[index] - array[index - 1])
        index += 1
    return delta_encoded


def delta_decoding(array: list[int]):
    delta_decoded: list[int] = [array[0]]
    index = 1
    while index < len(array):
        delta_decoded.append(array[index] + delta_decoded[index - 1])
        index += 1
    return delta_decoded


def missing_encoding(array: list[int]):
    maximum: int = max(array)
    res: list[int] = []
    for i in range(maximum):
        if i not in array:
            res.append(i)
    return res


def relative_encoding(array: list[int]):
    base_array: list[float] = []
    minimum = min(
        filter(lambda x: x != 0, array)
    )  # excluding 0 which one is the minimum
    minimum_i = array.index(minimum)
    base_array = array[0 : minimum_i + 1]  # type: ignore
    for element in array[minimum_i + 1 :]:
        base_array.append(element / minimum)
    return base_array


def shanon_score(array: list[Any]):
    """Calculate how much can we compress the payload and how much entropy it have"""
    unique_elements = set(array)
    length = len(array)
    probabilities: dict[Any, float] = {}
    for element in unique_elements:
        probabilities[element] = array.count(element) / length
    return -sum(map(lambda pi: pi * log(pi, 2), probabilities.values()))


def log_decomposition(remainder: float, base: float = 2):
    parts: list[float] = []
    while remainder > 0:
        exponent, remainder = ilog(base, remainder)
        parts.append(exponent)
    return sorted(parts), remainder


def log_composition(exponents: list[float], base: float = 2, remainder: float = 0):
    return sum([base**x for x in exponents]) + remainder


def chinese_flat_compressor(array: list[list[int]]):
    base: dict[int, list[int] | int] = {}
    for i, element in enumerate(array):
        if element[0] not in base:
            base[element[0]] = [i, element[1]]
        else:
            base[element[0]].append(i)  # type: ignore
            base[element[0]].append(element[1])  # type: ignore
    for element in base:
        base[element] = chinese_encoding(cast(list[int], base[element]))
    return base


def chinese_flat_decompressor(array: list[int]):
    pass


# utils
def number_to_bits(number: int):
    return [int(x) for x in bin(number)[2:]]


def bits_to_number(array: list[int] | str):
    return sum(map(lambda x: int(x[1]) * 2 ** x[0], enumerate(reversed(array))))


def chinese_encoding(array: list[int]) -> int:
    """ """
    prime_array: list[int] = [cast(int, nextprime(max(array)))]
    while len(prime_array) < len(array):
        prime_array.append(cast(int, nextprime(prime_array[-1])))
    assert len(prime_array) == len(
        array
    ), "Modulis length is not equal to remainders length"
    crt_result = crt(prime_array, array, check=True)
    if not crt_result:
        raise ArithmeticError("Something is wrong on teh CRT algorithm encoding")
    crt_value = crt_result[0]
    assert all(
        [x == crt_value % prime_array[i] for i, x in enumerate(array)]
    ), "This operation werent reversable"
    # result = value % BOUND
    return crt_value


# algorithms
def flat_encoding(array: list[int]):
    flatted_array: list[list[int]] = []
    for element in array:
        if len(flatted_array):
            target = flatted_array[-1]
            if target[0] == element:
                target.append(0)
            elif element - sum(target) == 1:
                target.append(1)
            else:
                flatted_array.append([element])
        else:
            flatted_array.append([element])
    for arr in flatted_array:
        if len(arr) > 1:
            arr[1] = bits_to_number([1, *arr[1:]])
            if len(arr) > 2:
                del arr[2:]
        else:
            arr.append(0)
    return flatted_array


def flat_array(array: list[list[Any]]):
    flattened: list[Any] = []
    for el in array:
        flattened.extend(el)
    return flattened


def unflat_array(array: list[Any]):
    fat_array: list[Any] = []
    for i in range(0, len(array), 2):
        fat_array.append([array[i], array[i + 1]])
    return fat_array


def flat_decoding(array: list[list[int]]):
    res: list[int] = []
    for element in array:
        res.append(element[0])
        if element[1]:  # If 0 means nothing was added at all
            behaviour = number_to_bits(element[1])
            behaviour.pop(0)  # remove delimiter
            for i, b in enumerate(behaviour):
                if b == 0:
                    res.append(element[0])
                elif b == 1:
                    res.append(element[0] + sum(behaviour[:i]) + 1)
    return res


def delta_reduction(array: list[int]):
    full_delta_encoded = array.copy()
    times = 0
    while True:
        new_delta_encoded = delta_encoding(array=full_delta_encoded)
        if new_delta_encoded[1] < 0:  # when there is no further change on the payload
            break
        times += 1
        full_delta_encoded = new_delta_encoded
    return full_delta_encoded, times


def delta_expansion(array: list[int], times: int = 1):
    full_delta_decoded = array.copy()
    while times > 0:
        full_delta_decoded = delta_decoding(array=full_delta_decoded)
        times -= 1
    return full_delta_decoded


def place_encoding(
    array: list[int],
):
    temp_struct: dict[int, list[int]] = {}
    last_el = -1
    assert last_el not in array, "SW Place Encoding"
    for i, el in enumerate(array):
        if el not in temp_struct:
            temp_struct[el] = [i]
            last_el = el
        elif last_el != el:
            temp_struct[el].append(i)  # type: ignore
            last_el = el
    places: list[int] = []
    for el in temp_struct:
        temp_struct[el] = delta_encoding(temp_struct[el])
    for element in temp_struct:
        places.append(
            chinese_encoding([len(temp_struct[element]), *temp_struct[element]])
        )
    return places


def alien_compressor(array: list[int]):
    pass


def pack_to_bytes(array: list[int], remainder: Optional[int] = None):
    """
    Each element of the array is part of the flat decoding algorithm therefore we need to treat each element as a byte
    """
    pass


def bit_packing(array: list[int]):
    """
    Store the bytes in each bit
    """
    pass


def succession_count(array: list[int]):
    res: list[int] = []
    last_el: Optional[int] = None
    for el in array:
        if el != last_el:
            res.append(0)
        else:
            res[-1] += 1
        last_el = el
    return res, set(array)


def counter_strike(array: list[int]):
    counter = Counter(array)
    commons = counter.most_common()
    Zs = commons[0][0]
    Os = commons[1][0]
    # the rest of the numbers are going to take 0s as its value and therefore will be marked in a position matrix.
    binary_array: list[Literal[1, 0]] = []
    position_matrx: dict[int, list[int]] = {}
    for i, element in enumerate(array):
        if element == Os:
            binary_array.append(1)
        else:
            if element != Zs:
                if element not in position_matrx:
                    position_matrx[element] = [i]
                else:
                    position_matrx[element].append(i)
            binary_array.append(0)
    return bits_to_number(cast(list[int], binary_array)), position_matrx


def make_number(array: list[float]):
    res: list[int] = []
    for el in array:
        for i in range(el - len(res)):
            res.append(0)
        res.append(1)
    return bits_to_number(res[::-1])


def unmake_number(number: int):
    res: list[int] = []
    for i, v in enumerate(number_to_bits(number)[::-1]):
        if v == 1:
            res.append(i)
    return res


def compress(log_base: float = 1.15, rand_bytes: int | None = 4, payload: bytes = None, **kwargs):  # type: ignore
    assert (
        log_base > 1
    ), "Log base must be higher than 1 to aviod both Math domain error and infinite loop"
    if rand_bytes:
        data = payload or randbytes(rand_bytes)
        numeric_data = int.from_bytes(data, "big")
        print(f"@-> Byte input {data}")
        print(f"@-> Numeric Convertion input {numeric_data}")
        print(f"@-> Byte Length: {len(data)} bytes")
        print(f"@-> Shanon Score #0 {shanon_score(list(data))}")
        # Step #1: Generate entropy and convert the input into an array with pattern.
        encoded_data_log, remainder = log_decomposition(numeric_data, base=log_base)
        r_encoded_data_log = log_composition(
            encoded_data_log, log_base, remainder=remainder
        )
        assert (
            r_encoded_data_log == numeric_data
        ), f"Error on log decomposition #1 {r_encoded_data_log} is not {numeric_data}"  # step #1 check
        print(f"@-> Shanon Score #1 {shanon_score(encoded_data_log)}")
        print(f"@-> Log Decomposition max result is: {max(encoded_data_log)}")
        # Step #2: Make a number array from the bit index array in the log decomposition step
        print(encoded_data_log)
        encoded_data_number = make_number(encoded_data_log)
        assert (
            unmake_number(encoded_data_number) == encoded_data_log
        ), "Error on make a number from smaller base #2"

        # Step #2: Delta encoding, reduce payload components size
        # encoded_data_delta = delta_encoding(encoded_data_log)
        # assert delta_decoding(encoded_data_delta) == encoded_data_log, "Error on delta encoding #2" # step #2
        # data_shsc = shanon_score(encoded_data_delta)
        # print(f"@-> Shanon Score #2 {data_shsc}")
        # Step #3 Encoding basic patterns found in the reduced payload and any existing entropy
        # encoded_data_flat = flat_encoding(encoded_data_delta)
        # assert flat_decoding(encoded_data_flat) == encoded_data_delta, "Error on delta encoding #4"
        # data_shsc = shanon_score(flat_array(encoded_data_flat))
        # print(f"@-> Shanon Score #3 {data_shsc}")
        # Step #-1 Packing and cleaning
        # full_encoded = encoded_data_delta
        # print(f"""@-> Expected size after compression with shanon thereom: {(data_shsc*len(full_encoded))/8} bytes""")
        # print(f"@-> Current size on data: {(sum([x.bit_length() for x in full_encoded]) + (remainder.bit_length() if remainder else 0))/8} bytes")
        # print(f"@-> Current raw size on data: {len(full_encoded) + (remainder.bit_length() if remainder else 0)/8} bytes")
        return encoded_data_number, remainder
    return None


# In 2 bits we could store either 00 for 1 byte, 01 for binary (1 and 0, 2 bits) bits, 10 (2) for 4 bits and 11 (3) for 6 bits.
