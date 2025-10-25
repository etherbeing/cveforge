DECIMAL_BASE = 10


def get_last_digit(number: float, precision: int = 16):
    last_digit: int = 0
    number = abs(number)
    number = int(number * DECIMAL_BASE**precision)
    while number != 0:
        number, last_digit = divmod(number, DECIMAL_BASE)
        if last_digit != 0:
            break
    return last_digit


def append_digit(number: float, value: int, index: int):
    return (number * DECIMAL_BASE ** (index + 1) + value) / (
        DECIMAL_BASE ** (index + 1)
    )
