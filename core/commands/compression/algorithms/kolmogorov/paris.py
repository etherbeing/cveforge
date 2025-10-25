def kparis(numeric_value: int, group_size: int = 2**8):
    """It doesnt work :-) entropy is hard to beat"""
    remainder: int = numeric_value
    bit_length = numeric_value.bit_length()
    bit_max_value = 2**bit_length
    parts: list[int] = []
    while remainder > 0:
        bounded_relation = (remainder * group_size) // bit_max_value
        reversable_val: int = (bounded_relation * bit_max_value) // group_size
        if reversable_val == 0:
            break  # avoid infinite loop
        parts.append(bounded_relation)
        remainder = remainder - reversable_val
        bit_max_value = (
            (bit_max_value - reversable_val) * bounded_relation
        ) // group_size
    # reverse = unkparis(parts, bit_length, group_size)
    # assert reverse == numeric_value, f"Lossy compression made {reverse-numeric_value}"
    return parts, remainder


def unkparis(values: list[int], bit_length: int, group_size: int = 2**8):
    bit_max_value = 2**bit_length
    number: int = 0
    for percent in values:
        val = (percent * bit_max_value) // group_size
        number += val
        bit_max_value = val
    return round(number)
