from .manipulation import ilog


def log_decomposition(remainder: float, base: float = 2):
    parts: list[float] = []
    while remainder > 0:
        exponent, remainder = ilog(base, remainder)
        parts.append(exponent)
    return sorted(parts), remainder
