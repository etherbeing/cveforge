"""
In this attempt #wtv we are gonna try to use Taylor series to compress the payload:
Idea:
x+x**2/2+x**3/3 and so on
"""

from math import factorial

from sympy import Symbol


def taylor(x: int, precision: int = 10):
    t = Symbol("x")
    tv: Symbol = 0  # type: ignore
    res = 0
    for element in range(precision):
        res += ((-1) ** element * (x ** (2 * element + 1))) / factorial(2 * element + 1)
        tv += ((-1) ** element * (t ** (2 * element + 1))) / factorial(2 * element + 1)
    return res, tv, tv.evalf(subs={"x": x})
