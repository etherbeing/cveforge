"""
This is a continuation of the power algorithm, which real name is BER algorithm or Base Exponent and Remainder, algorithm.
An alternative name is Basic Exponential Reducer algorithm.

This file is going to be separated into some class functions.

1. Theory Tester Function, it does test the theory against different values and contibilize how much is the reduction in its minimum,
maximum and mean.
2. Utility functions, for example ilog, iroot, idecompose, and so on. These functions are intended to be used to handle whole integers
instead of floating numbers, for performance and compression integrity.

"""

import math
from dataclasses import dataclass
from typing import Any, Optional, cast

from prompt_toolkit import prompt
from sympy import root

from utils.tests import Testable

from .delta import compress


class BERCompressor:
    BASE_DEFAULT_SIZE: int = 2
    REMAINDER_DEFAULT_SIZE: int = 8
    EXPONENT_DEFAULT_SIZE: int = 2
    BIT_LENGTH_DEFAULT_SIZE: int = 2
    REMAINDER_SIGN_SIZE: int = 1

    @dataclass
    class Stats:
        mean = 0
        min = 0
        max = 0
        compression_starts = 0

    chunk_size: int = 512  # bytes
    BYTE_SIZE: int = 8

    def __init__(self, payload: bytes) -> None:
        self._payload = payload
        self.stats = self.Stats()

    def compress(self):
        # bit_size = self.chunk_size*self.BYTE_SIZE
        compressed_payload: bytes = bytes()
        for chunk in range(0, len(self._payload), self.chunk_size):
            chunk_int: int = int.from_bytes(
                self._payload[chunk : chunk + self.chunk_size]
            )
            compressed_parts: list[int] = iauto(chunk_int)
            # order is:
            # 1. base (defaults to 2 bytes, could be modified by bit length parameter)
            # 2. remainder (4 bytes)
            # 3. exponent (defaults to 2 bytes, could be modified by bit length parameter, if exponent is 2 is a natural exponent meaning
            # it will be represented by bit 0, using exponent 0 to represent the bit 1 is unlikely therefore we dont need to compress one
            # bit as is the minimum unit for computational purposes nowadays until quantum computers are out )
            # 4. remainder sign (1 bit for 0 negative, and 1 positive, defaults to 1)
            # 5. bit length (1 byte)
            # 6. depth (just one bit of 1 means it recursive but not how much, it could hold up to 1 byte)
            #
            # The maximum payload size it would be if all bits occupied and using standard body: 10 bytes and 1 bit
            compressed_payload = compressed_parts[0].to_bytes(
                compressed_parts[0].bit_length() // 8 + 1, byteorder="big"
            )  # base
            compressed_payload += int.to_bytes(
                compressed_parts[1], length=self.REMAINDER_DEFAULT_SIZE, byteorder="big"
            )  # remainder
            compressed_payload += int.to_bytes(
                compressed_parts[2], length=self.EXPONENT_DEFAULT_SIZE, byteorder="big"
            )  # exponent
            compressed_payload += bool.to_bytes(
                compressed_parts[1] < 0,
                length=self.REMAINDER_SIGN_SIZE,
                byteorder="big",
            )  # remainder sign
            compressed_payload += int.to_bytes(
                compressed_parts[3],
                length=self.BIT_LENGTH_DEFAULT_SIZE,
                byteorder="big",
            )  # bit length
            print(compressed_parts)
        return compressed_payload

    def decompress(
        self,
    ):
        pass


class TheoryTesterFunction(Testable):

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass

    @classmethod
    def test(
        cls,
    ):
        option = ""
        while option.lower() != "exit":
            option = prompt("Please input your desire option (help for more): ")
            if option == "help":
                print(
                    """
    ilog
    iroot
    compress
    decompress
    exit
    """
                )
            elif option == "ilog":
                print(
                    ilog(
                        int(prompt("Enter base number: ")),
                        int(prompt("Enter argument number: ")),
                    )
                )
            elif option == "iroot":
                print(
                    iroot(
                        int(prompt("Enter number: ")),
                        int(prompt("Enter root exponent number: ")),
                    )
                )
            elif option == "iauto":
                print(
                    iauto(
                        int(prompt("Enter number: ")),
                    )
                )
            elif option == "compress":
                kwargs: dict[str, Any] = {}
                rand_bytes = prompt("Enter byte amount: ")
                if rand_bytes:
                    kwargs["rand_bytes"] = int(rand_bytes)
                log_base = prompt("Enter log base: ")
                if log_base:
                    kwargs["log_base"] = int(log_base)
                print(compress(**kwargs))
            elif option == "decompose":
                print(idecompose(int(prompt("Enter your number: "))))
            elif option == "flog":
                print(flog(int(prompt("Enter a number: "))))
            elif option == "test":
                for i in range(1024):
                    pass


def ilog(base: int, argument: int, is_below: bool = True) -> list[int]:
    """
    Optimized logarithm operation for integers.

    Example usage:
    ```python
    ilog(2, 4) # Returns [2, 0]
    ilog(10, 101) # Returns [2, 1]
    ilog(2, 5) # Returns [2, 1]
    ilog(3, 17) # Returns [2, 8]
    ```

    :param base: The base of the logarithm (e.g. For a netherian logarithm the base is euler)
    :param argument: The argument of the logarithm (e.g. For a logarithm of base 10 we could use an argument of 10 such that the
    :param is_below: Whether the remainder is close from 0 to the power or from infinity to the power, if is_below flag is set to True
    (the default) then the remainder is positive, else is negative.
    logarithm is 2, meaning 10**2 is 100)
    :return: Returns a list containing the exponent at the index 0 and the remainder at the index 1 such that
    base**return[0]+return[1] is argument
    :rtype: list[int]
    """
    if base == 0 and argument != 0:
        raise ValueError("0 multiplied any times is going to return 0")
    exponent = 1
    virtual_base = base
    while True:
        virtual_base *= base
        if virtual_base > argument and is_below:
            break
        elif virtual_base < argument and not is_below:
            break
        elif virtual_base == argument:
            return [exponent + 1, 0]
        exponent += 1
    return [
        exponent,
        (base**exponent) - argument if not is_below else argument - (base**exponent),
    ]


def iroot(value: int, exponent: int = 2) -> list[int]:
    """Gives the nth root for the given value
    :param value: The value from which we wish to obtain the root.
    :param exponent: The nth root value or exponent similar to value**(1/exponent)
    :return: A list containing two value, first value the base of the exponent (e.g. iroot(4, 2) [2, 0]) and the
    second index is for the remainder of the root (remember we are working just with integers), for example the square root for 5 is
    [2, 1] as 2**2 is 4 and left a remainder of 1.
    """
    r = int(root(value, exponent))
    return [r, value - r**exponent]
    # return select(2, value//2, value, power=exponent)


def idecompose(value: int):
    bit_length = value.bit_length()
    # compression goal is less than bit_length
    parts: list[int] = []
    global_remainder = 0
    exponent = bit_length // 8
    while True:
        base, remainder = iroot(value, exponent)
        assert (
            base**exponent + remainder == value
        ), "Something is wrong at this point this should be the same"
        if base == 1:
            global_remainder = value
            break
        parts.append(base)
        if remainder == 0:
            break
        assert value != remainder, "Infinite loop detected"
        value = remainder
    return parts, global_remainder


def array_to_number(array: list[int]):
    max_bits = max(array).bit_length()
    assert max_bits <= 8, "Working in integers higher than 1 byte is not yet supported"
    payload = b""
    for x in array:
        payload += x.to_bytes(1, "big")
    return int.from_bytes(payload)


def number_to_array(number: int, estimated_maximum: int = 255) -> tuple[int]:
    bt_array: bytes = number.to_bytes(estimated_maximum, "big")
    starting_point = bt_array.rindex(b"\x00") + 1
    return cast(tuple[int], tuple(bt_array[starting_point:]))


def logarithmic_reduction(number: int, base: int, do_assert: bool = True):
    _number = number
    exponents: list[int] = []
    remainder: int = 0
    while (
        True
    ):  # e.g While e**x which is 2 isnt _value which is e**2 then this keeps on
        exponent, number = ilog(base, number)
        sign = number < 0 and -1 or 1
        exponents.append(
            exponent * sign
        )  # Store only 4 decimals points e.g. we store 2*10**4=20_000
        if exponent == 0 or number <= base:
            remainder = number
            break
    if (
        do_assert
    ):  # For debugging purposes only this should work if assertion is rised a problem is found in here
        test = 0
        for exponent in exponents:
            test += base**exponent
        test += remainder
        assert (
            test == _number
        ), f"This reduction is not reversable {test} is not {_number}, remainder is: {remainder}"
    return exponents, remainder


def binaryzate(array: list[int]):
    temp: set[int] = set()
    repetitions: list[int] = []
    # FIXME THERE IS AN ERROR IN THE ALGORITHM WE CANNOT RECUSIVELLY ITERATES AS WE ARE LOSING INFORMATION EACH TIME WE DO IT
    copied: list[int] = sorted(set(array))  # In order to count and so on
    if max(copied) >= 2**8:
        raise ValueError(
            "We cannot binaryzate an array of numbers higher than maximum binary size"
        )
    for x in copied:
        temp.add(
            x
        )  # t and e even though they appear like not they actually share the same size
        repetitions.append(array.count(x))

    return list_to_bits(temp), repetitions if max(set(repetitions)) > 1 else None


def flog(
    _value: int, base: Optional[int] = None, compression_pressure: int = 8
):  # e.g. _value=e**2
    base = (
        base or _value.bit_length()
    )  # This pressure works as pressing over the number structure down
    value: int = (
        _value  # A copy of the number for later modifications and keeping the original number
    )
    estimated_final_size_bits = 0
    print(f"@-> Stats: {value.bit_length()} bits; {value.bit_length()/8} bytes")
    # #1 Goal: To reduce maximum exponent size for binaryzation
    exponents, remainder = logarithmic_reduction(value, base)
    estimated_final_size_bits += remainder.bit_length()
    # #2 Goal: To filter array into binaryzed arrays
    binaryzed, repetitions = binaryzate(exponents)
    estimated_final_size_bits += binaryzed.bit_length()

    if repetitions:
        estimated_final_size_bits += sum([x.bit_length() for x in repetitions])
        repetition_number: int = array_to_number(repetitions)
        rn_log_exponents, rn_log_remainder = logarithmic_reduction(
            repetition_number, base**base
        )
        binaryzed_rn_log, rn_log_repetitions = binaryzate(rn_log_exponents)
    print(
        f"@-> Compressed Stats: {estimated_final_size_bits} bits; {estimated_final_size_bits/8} bytes"
    )
    compressed: list[int] = []
    # NOTE Lets split up the problem in parts, first we have a list of exponent that added up sums to the original number _value + remainder
    # Second we are trying to binaryze all the compositions of the exponents by creating an entropy array (as is likely that there is too
    # many entropy at this point due to the high pressure). The problem here is that the entropy array cannot be sorted as its positions
    # is information to us that cannot be losed.
    # Therefore,
    # TODO Before each member use 1 byte containing its last bit as the extension flag and the rest for setting the length of the next field
    # meaning we need to add 8 bits per compression component, 2**7-1 is 127 but we can just use 0 as 1 and calculate the data as 2**7
    # because no 0 is needed here (no length of 0 is needed), then the last bit tell use if the next component is higher than 128 or not
    # Struct of the payload
    # 1. Each part is contained by a header and a component, the header contain the size of the component, while the component the payload
    # 2. Each header is 1 byte in size, but only use its first 7 bytes for storing the length as the last bit is for extending the header's
    # size
    # 2.1. From the second header onwards we mostly use 6 bits instead and the 7th bit means whether to fix the header size to this one
    # last header size given.
    # 3. The first part is also the main part containing the payload most important part of the compression.
    # 3.1. The first part is header+paylaod and mostly the only part that needs an extension.
    # 3.2. The paylaod is encoded using the BER encoding algorithm, this algorithm works as follows.
    # 3.2.1. BER Encoding algorithm
    # Given an integer X (obtained from payload's bytes), we recursively obtain its logarithms
    # (the base is depending on the compression pressure parameter defaults to 17[no special reason]). Each integer logarithm let us
    # a remainder due to hardly obtaining an exact payload but anyways. This previous process leave us with a decendant array of
    # integers (perhaps with some repeated numbers). After this we need to normalize the repetition arrays, for this we recursively
    # apply the same algorithm to the repetition arrays, until we got an array of perhaps just 2 numbers or less.
    # The more important part is the way we use to encode this arrays is by binaryzing the arrays (new concept), this consist on
    # turning the set (without repeated numbers, remember repeated numbers was spread through repetion arrays). At the end we got
    # an array of binaryzed arrays (like integers). We store the arrays in inverse order for faster decompression.
    # Inverse process:
    # Given the array of binaryzed arrays we start by reading the first byte of the compressed payload, from there we obtain the
    # size of the first bynarized repetition array.
    #

    payload: bytes = b""
    remainder_size = math.ceil(remainder.bit_length() / 8)
    payload += remainder_size.to_bytes(1, "big")
    payload += remainder.to_bytes(remainder_size, "big")
    last_repetition = list_to_bits(set(exponents))
    last_repetition_size = math.ceil(last_repetition.bit_length() / 8)
    payload += last_repetition_size.to_bytes(1, byteorder="big")
    payload += last_repetition.to_bytes(last_repetition_size, "big")
    for component in reversed(compressed):
        size = math.ceil(component.bit_length() / 8)
        payload += size.to_bytes(1, byteorder="big")  # header
        payload += component.to_bytes(size, byteorder="big")
    print(f"Payload reduced by: {100-(len(payload)*8*100)/(_value.bit_length())}%")
    print(compressed, last_repetition, remainder)
    assert (
        reflog(payload) == _value
    ), "Decompressed payload is not the same as compressed one, so data was lost during decompression"
    assert len(exponents) == len(
        set(exponents)
    ), "TODO FIXME Later and avoid breaking the loop above when this condition isnt false yet"
    return payload


def reflog(payload: bytes):
    index = 0
    result: int = 0
    components: list[int] = []
    while True:
        if len(payload) <= index:
            break
        header = payload[index]  # 1 bytes
        component: int = int.from_bytes(
            payload[index + 1 : index + header + 1], "big"
        )  # n bytes from header index + 1 up to index + 1 + header
        components.append(component)
        index += header + 1
    remainder = components[0]
    repetition_array = bits_to_list(components[1])
    raw_components: list[list[int]] = []
    for index, component in enumerate(components):
        raw_components.append(bits_to_list(component))
    # lets expand now all the payload using the repetion arrays.
    print(remainder, repetition_array, raw_components)
    # Dynamically expanding the raw components
    i = 0
    while True:
        offset = 0  # used in order to keep track of the array expansion movements
        prev_expansor: list[int] = raw_components[i]
        expanding: list[int] = raw_components[i + 1]
        for index, repetitions in enumerate(prev_expansor):
            target = expanding[index + offset]
            offset += repetitions - 1
            for _ in range(repetitions - 1):
                expanding.insert(index, target)
        index += 1
        if index >= len(repetition_array):
            break
    print(remainder, repetition_array, raw_components)
    return result


def list_to_bits(array: set[Any], base: int = 2):
    # bit_array_length = math.ceil(math.log(max(array), 2))
    return sum(map(lambda x: base**x, array))  # 2 is the binary base


def bits_to_list(binaryzed_array: int, base: int = 2):
    array: list[int] = []
    index = 0
    while binaryzed_array > 0:
        if binaryzed_array & 1:
            array.append(index)
        index += 1
        binaryzed_array >>= 1
    return array


def iauto(value: int, bit_length: Optional[int] = None):
    """
    Automatically returns an exponential representation of a number.
    Struct:
    Base of the components (2 byte or bit length)
    Remainder of the components (Variable, ideally 2 bytes)
    Exponent of the components (2 byte or bit length)
    Bit length of the components (1 byte)

    Any omitted value is thought to be its default value
    Total payload minimum size:
    7 bytes. Meaning we can just start compressing from 2**(7*8) onwards.
    Still we can compress fewer numbers by using the bit length operator.
    """
    initial_exponent = 2
    minimum = 2  # The minimum value is always 2 as 1 powered by anything is just 1
    default: list[int] = iroot(
        value, initial_exponent
    )  # The maximum value is the square root given that the square root powered by any higher root is going to
    # be too much.
    maximum = 2 ** (1 * 8) - 1  # Or 1 bytes whole
    parts = 4
    bit_length = bit_length or value.bit_length() // parts
    compressed = [default[0], default[1], initial_exponent, bit_length]
    min_base, min_remainder, min_exponent = default[0], default[1], initial_exponent
    base, remainder = 0, 0
    # quick sort algorithm like again
    for exponent in range(minimum, maximum):
        base, remainder = iroot(value, exponent)
        if (
            remainder.bit_length() < bit_length and base < 2**bit_length - 1
        ):  # We found an acceptable value
            # COMPRESSION SUCCESSFULY DONE
            min_base = base
            min_remainder = remainder
            min_exponent = exponent
            break
        elif abs(remainder) < min_remainder:
            min_remainder = remainder
            min_base = base
            min_exponent = exponent

    compressed[0] = min_base
    compressed[1] = min_remainder
    compressed[2] = min_exponent
    return compressed


def select(minimum: int, maximum: int, target: int, power: int = 1) -> list[int]:
    """
    Seek for a number inside a range of numbers for a condition to be True

    :return: A list containing at index 0 the estimated target and at index 1 the remainder
    :rtype: list[int]
    """
    mp = (minimum + maximum) // 2
    while True:
        if target > mp**power and minimum != mp:
            minimum = mp
        elif target < mp**power and maximum != mp:
            maximum = mp
        elif maximum == mp or minimum == mp:  # No change on mp
            break
        else:
            return [mp, 0]
        mp = (minimum + maximum) // 2
    return [mp, target - mp**power]
