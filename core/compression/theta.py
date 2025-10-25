from math import ceil
from typing import Any


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
    exponent = 1
    if base == 0 and argument != 0:
        raise ValueError("0 multiplied any times is going to return 0")
    elif base == argument:
        return [exponent, 0]
    elif argument == 1:
        return [0, 0]

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


def binaryzate(array: list[int]):
    positions: list[list[int]] = []
    # FIXME THERE IS AN ERROR IN THE ALGORITHM WE CANNOT RECUSIVELLY ITERATES AS WE ARE LOSING INFORMATION EACH TIME WE DO IT
    header: set[int] = set(array)  # In order to count and so on
    positions = [[] for _ in header]
    empty_positions = True
    for i, x in enumerate(sorted(header)):
        last_index = 0
        while True:
            try:
                last_index = array.index(x, last_index)
            except ValueError:
                break
            positions[i].append(last_index)
            last_index += 1
        if len(positions[i]) > 1:
            empty_positions = False
    resulting_positions: list[int] = []
    for position in positions:
        resulting_positions.append(
            list_to_bits(set(position))
        )  # We can assure that is a set as we are talking about indexes here
    return list_to_bits(header), resulting_positions if not empty_positions else None


# Bitalize and Unbitalize are contrary operations meaning one denies the other


def bitalize(array: list[int]):
    "Turn an set into a bit array"
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


def compress(value: bytes, base: int = 10):
    numeric_value = int.from_bytes(value)
    remainder = numeric_value
    exponents: list[int] = []
    while remainder > base:
        exponent, remainder = ilog(base, remainder)
        exponents.append(exponent)
    assert (
        sum(map(lambda x: base**x, exponents)) + remainder == numeric_value
    ), "Something wrong in the calculations step #1"
    header = set(exponents)
    raw_components: list[int] = []
    for element in header:
        raw_components.append(exponents.count(element))
    assert (
        sum(map(lambda x: raw_components[x[0]] * base ** x[1], enumerate(header)))
        + remainder
        == numeric_value
    ), "Something wrong in the calculations step #2"
    int_header = bitalize(list(header))
    assert all(
        [bin(int_header)[2:][::-1][x] == "1" for x in header]
    ), f"Something is wrong in the processing on step #3 {bin(int_header)} {header}"
    compression_parts: list[int] = []
    compression_parts.append(remainder)
    compression_parts.append(int_header)
    print(f"Exponents were: {exponents}")
    print(f"Compression Payload so far: {compression_parts}")
    compression_size = sum([x.bit_length() for x in compression_parts])
    print(f"Compression Size so far: {compression_size}")
    print(f"The actual payload size is: {numeric_value.bit_length()}")

    print(f"We have yet to compress: {raw_components}")
    print(f"We have yet to compress(sorted): {sorted(raw_components)}")
    print(
        f"We have yet to compress(bits): {sum([x.bit_length() for x in raw_components])}"
    )
    print(
        f"Remaining available bit size is: {numeric_value.bit_length() - compression_size}"
    )
    if (
        len(set(raw_components)) == 1 and raw_components[0] == 1
    ):  # means all 1s no numer is repeated
        if remainder == 0:
            assert (
                int_header != numeric_value
            ), "No smaller representation for the given input? We couldn't compress this"
            return int_header.to_bytes(ceil(int_header.bit_length() / 8), "big")
    int_components: list[int] = []
    repetition_array = raw_components
    while True:
        int_part, repetition_array = binaryzate(repetition_array)
        int_components.append(int_part)
        if repetition_array == None:
            break
    print(
        "Bit length of the int componets: %s"
        % sum([x.bit_length() for x in int_components])
    )
    print("Int components %s" % int_components)
    assert (
        compression_size < numeric_value.bit_length()
    ), "We couldn't compress instead we expanded it"
    return b""
