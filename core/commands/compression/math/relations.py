from decimal import Decimal, getcontext
from math import log

# from core.commands.compression.math.utils import append_digit


def ratio(part: int, total: int):
    return part / total


def inverse_ratio(ratio: float, total: int):
    return ratio * total


def log_ratio(log_part: float, ratio_part: float, bit_length: int, base: int = 2):
    """Use this to estimate maximum precision or fair enough precision of the given Xs"""
    getcontext().prec = 512
    r = Decimal(base**log_part) / base**bit_length
    l = Decimal(log(base**bit_length * r, base))
    estimated_xs = r * base**bit_length, base**l
    return log_part, l, ratio_part, r, estimated_xs
