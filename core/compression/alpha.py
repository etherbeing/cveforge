from typing import Iterable


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


def normalize_array(array: Iterable[int]):
    base = min(array)
    return base, [x - base for x in array]


def array_to_matrix(array: list[int]):
    header = sorted(set(array))
    components: list[list[int]] = [[] for _ in header]
    for index, element in enumerate(header):
        last_index = 0
        while True:
            try:
                last_index = array.index(element, last_index)
                components[index].append(last_index)
                last_index += 1
            except ValueError:
                break
    normalized_header = normalize_array(header)
    int_header = bitalize(normalized_header[1])
    int_list_components: list[int] = []
    for indexes in components:
        normalized_indexes = normalize_array(indexes)
        int_list_components.append(bitalize(normalized_indexes[1]))
    return int_header


def matrix_to_array(array: list[int]):
    pass


def compress_protocol(value: int):
    header: int = value.bit_length()  # 8 bits long
    component: int = value  # header size and varies
    return header.to_bytes() + component.to_bytes()


def decompress_protocol(value: int):
    return value


def compress(value: bytes, chunk_size: int = 512):
    parts: list[bytes] = []
    for chunk in range(0, len(value), chunk_size):
        parts.append(_compress(value[chunk : chunk + chunk_size]))
    return b"".join(parts)


def _compress(value: bytes):
    REMAINDER_SIZE: int = 4  # bytes
    BYTE_SIZE: int = 8  # bits

    try:
        numeric_value = int(value)
    except ValueError:
        numeric_value = int.from_bytes(value, "big")
    print(
        f"Payload stats: {numeric_value.bit_length()} bits; {numeric_value} numeric value, {len(value)} bytes"
    )
    remainder = numeric_value
    logs: list[int] = []
    signs: list[int] = []
    base = max(2, 2 ** (numeric_value.bit_length() // 256))
    while True:
        exponent, remainder = ilog(base, remainder)
        if remainder <= 0:
            signs.append(len(logs))
        remainder = abs(remainder)
        logs.append(exponent)
        if remainder.bit_length() < REMAINDER_SIZE * BYTE_SIZE:
            break
    array_to_matrix(logs)
    assert (
        sum(map(lambda x: base**x, logs)) + remainder == numeric_value
    ), "Wrong calculations at step #1"
    base_value = int(min(logs))
    logs = list(map(lambda x: x - base_value, logs))
    assert (
        sum(map(lambda x: base ** (x + base_value), logs)) + remainder == numeric_value
    ), "Wrong calculations at step #2"
    exponents = bitalize(logs)
    assert logs == unbitalize(
        exponents
    ), f"Unbitalize operation failed to successfully operate at step #3, logs: {logs} is not {unbitalize(exponents)}, {exponents} is the bitalized exponents"
    signs_matrix = bitalize(signs)
    assert signs == unbitalize(
        signs_matrix
    ), f"Unbitalize operation failed to successfully operate at step #4, signs: {signs} is not {unbitalize(signs_matrix)}, {signs_matrix} is the bitalized signs"
    assert (
        _restore(
            base_value=base_value,
            exponents=exponents,
            signs=signs_matrix,
            remainder=remainder,
        )
        == numeric_value
    ), f"Cannot restore the data due to some calculation error perhaps"
    print(sum(x.bit_length() for x in [remainder, base_value, exponents, signs_matrix]))
    return (
        remainder.to_bytes()
        + base_value.to_bytes()
        + exponents.to_bytes()
        + signs_matrix.to_bytes()
    )


def _restore(base_value: int, exponents: int, signs: int, remainder: int):
    # #1 Exponents to list
    exponents_list = list(map(lambda x: x + base_value, unbitalize(exponents)))
    signs_list = unbitalize(signs)
    for sign in signs_list:
        exponents_list[sign] *= -1
    result = 0
    for exponent in exponents_list:
        result += 2**exponent
    return result + remainder


# Lets do the compression with this payload for starting: compress(b'hello world my name is skrillex')
