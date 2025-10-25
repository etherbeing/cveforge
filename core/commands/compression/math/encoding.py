from .manipulation import ilog


def regressive_log_encoding(number: int | float, base: int):
    """Doesnt work ...."""
    # bt = number.bit_length()
    exs: list[int | float] = []
    facs: list[int | float] = []
    while base > 1:
        exponent, number = ilog(base, number)
        if len(exs) > 0 and exponent == exs[-1]:
            facs[-1] += 1
        else:
            exs.append(exponent)
            facs.append(1)
        base -= 1
    return exs, facs, number
