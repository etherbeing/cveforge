from random import randbytes


def gen_bytearray(length: int = 256):
    return randbytes(length)


def reduce(array: list[int]):
    minimum = min(array) - 1
    if minimum < 0:
        return array, 0
    return list(map(lambda x: x - (minimum), array)), minimum


def convert_to_base(array: list[int], base: int = 10):
    """
    For example:
    ```py
    array=[64, 1, 169, 133]
    array, reduced_base = reduce(array) # array, 0 as no reduction is possible
    numeric_value = convert_to_base(array) # 65923
    65933
    ``
     64_000
       1_00
      169_0
        133
    -------
      65923
    """
    return sum(
        map(lambda x: (base ** (len(array) - (x[0] + 1))) * x[1], enumerate(array))
    )


def convert_base_to_array(number: int, base: int = 10, array_length: int = 256):
    res_arr: list[int] = []
    # 1
    last_number = number % (array_length - 1)
    no = number - last_number
    no = no // base
    # 2
    second_number = (no - base) % array_length
    no = no - second_number
    no = no // base
    # 3
    third_number = no % base
    no = no - third_number
    no = no // 10
    return [no, third_number, second_number, last_number]


def log_decompose(value: int):
    pass
