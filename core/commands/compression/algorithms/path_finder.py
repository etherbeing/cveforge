"""
This file so far only encode doesnt compress, so is basically a failure (yet again :-)
"""


def path_finder_v0(number: int, speed: int = 2**8, _base: int = 2):
    """
    This is an encoder function so far as no compression is done here, try to improve it to make it show less clues than bytes existing
    """
    storage_size = _base ** number.bit_length()
    part_size: int = (
        storage_size // speed
    )  # work on integer domain, either way as far as speed is a multiple of 2 or a power of 2 (base).
    path: list[int] = []
    while part_size > 1:
        lps = part_size
        for part in range(speed):
            if (
                number >= part * part_size and number < (part + 1) * part_size
            ):  # means in range
                path.append(part)
                number = number - part * part_size
                # print(part_size) # This is just for testing purposes
                part_size = divmod(((part + 1) * part_size - part * part_size), speed)[
                    0
                ]  # readjust the size of this part
                break
        else:
            path.append(speed)
            part_size = ((speed) * part_size - (speed - 1) * part_size) // speed
            number = number - speed * part_size
        if lps == part_size:
            break  # Avoid infinite loop
    path.append(number)
    return path


def map_reader_v0(clues: list[int], bit_length: int, speed: int = 2**8, _base: int = 2):
    storage_size = _base**bit_length
    part_size: int = storage_size // speed  # work on integer domain
    remainder: int = clues.pop()
    result = 0
    bases: list[int] = []
    for clue in clues:
        # print(part_size)
        result = result + clue * part_size
        bases.append(clue * part_size)
        # print(clue*part_size)
        part_size = ((clue + 1) * part_size - clue * part_size) // speed
    return result + remainder
