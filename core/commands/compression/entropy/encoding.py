import logging


def delta_encoding(array: list[int]):
    delta_encoded: list[int] = [array[0]]
    index = 1
    while index < len(array):
        delta_encoded.append(array[index] - array[index - 1])
        index += 1
    return delta_encoded


def missing_encoding(array: list[int]):
    maximum: int = max(array)
    res: list[int] = []
    for i in range(maximum):
        if i not in array:
            res.append(i)
    return res


def necessary_encoding(number: int, base: int = 2):
    bit_length = number.bit_length()
    storage_size = base**bit_length
    floor = base ** (bit_length - 1)
    logging.debug("Storage Size is: %s", storage_size)
    logging.debug("Floor is: %s", floor)
    # means the number we need is between storage_size and floor
    necessary_data = storage_size - floor
    logging.debug("New size is: %s", necessary_data)
    logging.debug("New size's size is: %s bits", necessary_data.bit_length())
