def to_base(values: list[int], base: int = 10):
    res = 0
    for i, element in enumerate(values):
        res += base ** (len(values) - (i + 1)) * element
    return res


def binary_encode(number: int, speed: int = 2, _base: int = 2):
    """Doesnt work"""
    bottom = 0
    top = _base ** number.bit_length()
    target = 0
    encoded_values: list[int] = []
    rate_value: int = 0
    rate: bool = True
    while target != number:
        target = (top + bottom) // speed  # work with integers
        if target > number:
            top = target
            if rate:
                encoded_values.append(rate_value)
                rate_value = 0  # restart the rate
                rate = False
            rate_value += 1
        elif target < number:
            bottom = target
            if not rate:
                encoded_values.append(rate_value)
                rate_value = 0  # restart the rate
                rate = True
            rate_value += 1
        else:
            break
    result = to_base(encoded_values)
    return result, (result.bit_length() * 100) / number.bit_length()


def binary_decode(number: int, base: int = 10):
    pass
