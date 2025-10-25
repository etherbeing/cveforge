from math import ceil
from typing import Any, TypedDict


def decompose(value: int, base: int = 2):
    """
    Returns two factors for value that it can be represented using a notation of exponents, for example:
    decompose(16) = (2, 2), (2, 2), 0
    decompose(59) = (2, 2), (((2, 3,0), ( 2, 1)), 1), 1

    Step by step of decompose(59).
    1. Round it to an even number ~ 60
    2. 60-59=1 which is the last number 1 which is the correction to the original number
    3. Divide 60/2 which is 30 then we know 30*2 is 60, try again 30/2 is 15 so 15*4 is 60 then.
    4. Round 15 to its closest even number this is 16, then we got 16 and 4
    5. 16=8 * 2, 8 is 2**3 and 2 is 2**1 then
    """
    if not isinstance(value, int):  # type: ignore
        raise ValueError("You must provide us with an integer here")
    if value == 1:
        return (value, value, 0)  # This is the default factorization for 1
    elif base == 1 or base == 0 or value == 0:
        return (value, base, 0)  # This is a default return statement
    virtual_value = value  # Use this value for modifications and more leaving value intact so no modification is made over it
    eveness_correction = value % base
    is_even = eveness_correction == 0
    global_remainder = 0
    if not is_even:
        virtual_value = value + (base - eveness_correction)
        global_remainder = base - eveness_correction
    p1, p2 = virtual_value, 1
    while p1 % base == 0:
        p1 = p1 // base  # using floor division as we are looking for integers no floats
        p2 = p2 * base
        if p1 == p2:
            break  # A lot of reduction happened here
    return (p1, p2, global_remainder)


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
    temp: set[int] = set()
    repetitions: list[int] = []
    # FIXME THERE IS AN ERROR IN THE ALGORITHM WE CANNOT RECUSIVELLY ITERATES AS WE ARE LOSING INFORMATION EACH TIME WE DO IT
    copied: list[int] = sorted(set(array))  # In order to count and so on
    # if max(copied) >= 2**8:
    #     raise ValueError("We cannot binaryzate an array of numbers higher than maximum binary size")
    for x in copied:
        temp.add(
            x
        )  # t and e even though they appear like not they actually share the same size
        repetitions.append(array.count(x))

    return list_to_bits(temp), repetitions if max(set(repetitions)) > 1 else None


def exponential_flatting(array: list[int]):
    result: list[int] = array.copy()
    for i, b in enumerate(array):
        log_b = ilog(2, b)
        assert log_b[1] == 0, "We can just flat an array filled with powers of 2"
        result[i] = log_b[0]
    return result


def factorization_flatting(array: list[int], common_factor: int = 2):
    result: list[int] = array.copy()
    for i, b in enumerate(array):
        res, rem = divmod(b, 2)
        assert rem == 0, "We can just flat an array filled with factors of 2"
        result[i] = res
    return result


def array_to_numeric_matrix(array: list[int]):
    headers = set(array)
    columns: list[list[int]] = [[] for _ in headers]
    for index, header in enumerate(headers):
        last_index = 0
        while True:
            try:
                last_index = array.index(header, last_index) + 1
                columns[index].append(last_index)
            except ValueError:
                break
    compressed_columns: list[int] = []
    for column in columns:
        compressed_columns.append(binaryzate(column)[0])
    return binaryzate(list(headers))[0], compressed_columns


def list_cocktail(array: list[int]):
    base_value = min(array)
    base_index = array.index(base_value)


class FlogStruct(TypedDict):
    corrected: bool  # 1 bit telling us whether the payload was corrected or not, meaning is divisible by two or not
    global_remainder: int  # 1 byte integer
    columns_log_reduction: (
        int  # 1 byte integer, how many time we reduced the columns by log with base 2
    )
    columns_factorizations: (
        int  # 1 byte integer, how many times we factorized by 2 the columns
    )
    headers: (
        list[int] | int
    )  # 1 byte integer, for reading it gives a list of integer for writing expect an integer


class TracesStruct(TypedDict):
    tool: (
        bool  # False for a factor tool or True for a shrinker tool (decompose vs ilog)
    )


def struct_to_bytes(struct: FlogStruct):
    print(struct)
    payload: int = 0
    payload = payload | struct["corrected"]
    payload <<= 8
    payload |= struct["global_remainder"]

    return payload.to_bytes()


def bytes_to_struct(_payload: bytes) -> FlogStruct:
    payload: int = int.from_bytes(_payload, "big")
    return {
        "corrected": bool(payload & 0xF),
        "global_remainder": (payload << 1 & 0xFF),
        "headers": [],
        "columns_factorizations": 0,
        "columns_log_reduction": 0,
    }


def base(value: int, pressure: int = 8):
    _value = value
    expected_bit_size = 0
    payload_struct: FlogStruct = {
        "corrected": False,
        "global_remainder": 0,
        "headers": [],
        "columns_factorizations": 0,
        "columns_log_reduction": 0,
    }
    BYTE_LENGTH: int = 8
    base_log: int = max(ceil(value.bit_length() / 256), 2)
    initial_correction: bool = (
        _value % base_log != 0
    )  # Whether we need to correct the first decomposition of value to be a multiple of 2
    expected_bit_size += 1
    payload_struct["corrected"] = True
    headers_array: list[int] = []
    remainders: set[int] = set()
    while True:
        decomposition = decompose(value, base_log)
        headers_array.insert(0, decomposition[1])
        remainders.add(
            decomposition[2]
        )  # Push into the list the factor and the remainder (f*x+r)
        if decomposition[0] < base_log**BYTE_LENGTH:
            expected_bit_size += 8  # 8 bits reserved for this
            payload_struct["global_remainder"] = decomposition[0]
            break
        value = decomposition[0]
    headers = exponential_flatting(headers_array)
    while True:
        try:
            headers = factorization_flatting(headers)
        except AssertionError:  # FIXME dont use assertions in production
            break
    headers, columns = array_to_numeric_matrix(headers)
    # compressing now the columns
    while True:
        try:
            columns = factorization_flatting(columns)
            columns = exponential_flatting(columns)
        except AssertionError:
            break
    compressed_columns: list[int] = []
    for column in columns:
        if column.bit_length() > value.bit_length() / pressure:
            compressed_columns.append(base(column))
        else:
            compressed_columns.append(column)
    # is almost unprobable that there are repetitions i think
    print(columns)
    payload_struct["headers"] = headers
    # TODO further compress the columns into smaller chunks if possible but first TODO reverse the process so far
    return unbase(struct_to_bytes(payload_struct))
    expected_remainders = 2 if not initial_correction else 1
    if (
        len(set_universal_remainder) != expected_remainders
    ):  # With initial correction there should be 1 and 0 at the end
        raise ValueError(
            f"""We need to fix this as something seems wrong here, {len(set_universal_remainder)} is not {expected_remainders}, instead it contains {set_universal_remainder}, components {components}
Also payload is: {_value} which {'not' if not initial_correction else ''} needed initial correction as {_value}%{base_log} is {_value%base_log}
Which is {initial_correction}
"""
        )
    bases = list(map(lambda x: x[0], components))
    for i, b in enumerate(bases):
        log_b = ilog(base_log, b)
        assert log_b[1] == 0, "Just in case this should always be true"
        bases[i] = log_b[0]
    # We are going now to create a matrix for storing the positions and then using binaryzation on each column of the matrix
    header, columns = array_to_numeric_matrix(bases)
    payload_struct["header"] = header
    expected_bit_size += header.bit_length()
    pcc: dict[str, list[Any]] = {
        "headers": [],
        "columns": [],
    }  # processed compressed columns
    for index, column in enumerate(columns):
        stripped_column: list[int] = []
        unified_remainder: set[int] = set()
        while True:
            column_parts = decompose(column, base=base_log)
            stripped_column.append(ilog(2, column_parts[1])[0])
            unified_remainder.add(ilog(2, column_parts[2])[0])
            if column_parts[0] < base_log**BYTE_LENGTH:
                # NOTE Important data here is, the logs and the unified remainder, do we need something else?
                assert (
                    len(unified_remainder) == 1
                ), "We didnt handle here the case where is two for some reason (lazyness)"
                pcc_header, pcc_columns = array_to_numeric_matrix(stripped_column)
                pcc["headers"].append(pcc_header)
                pcc["columns"].append(pcc_columns)
                break
            column = column_parts[0]

    print(
        f"Partial compression: {expected_bit_size} bits of {_value.bit_length()} bits"
    )
    print(_value)
    print(payload_struct.__str__())
    print(
        "Compressed payload size so far: %s bits"
        % (expected_bit_size + sum(map(lambda x: x.bit_length(), columns)))
    )
    print(pcc)
    return _value


def unbase(value: bytes):
    _value: int = int.from_bytes(value, "big")
    return _value


def compress(value: bytes):
    try:
        v = int(value)
        print(f"@-> Before compression {v.bit_length()} bits")
        payload = base(value=v).to_bytes()
        print(f"@-> After compression {len(payload)} bytes")
        return payload
    except ValueError:
        print(f"@-> Before compression {len(value)} bytes")
        payload = base(value=int.from_bytes(value)).to_bytes()
        print(f"@-> After compression {len(payload)} bytes")
        return payload
