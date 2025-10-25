from collections import Counter


def ilog(base: float, argument: float, is_below: bool = True) -> list[float]:
    """
    Optimized logarithm operation for integers.

    Example usage:
    ```python
    ilog(2, 4) # Returns [2, 0]
    ilog(10, 101) # Returns [2, 1]
    ilog(2, 5) # Returns [2, 1]
    ilog(3, 17) # Returns [2, 8]
    ```

    :param base: The base of the logarithm (e.g. For a netherian logarithm the base is euler)
    :param argument: The argument of the logarithm (e.g. For a logarithm of base 10 we could use an argument of 10 such that the
    :param is_below: Whether the remainder is close from 0 to the power or from infinity to the power, if is_below flag is set to True
    (the default) then the remainder is positive, else is negative.
    logarithm is 2, meaning 10**2 is 100)
    :return: Returns a list containing the exponent at the index 0 and the remainder at the index 1 such that
    base**return[0]+return[1] is argument
    :rtype: list[int]
    """
    exponent = 1
    if base == 0 and argument != 0:
        raise ValueError("0 multiplied any times is going to return 0")
    elif base == argument:
        return [exponent, 0]
    elif argument == 1:
        return [0, 0]

    virtual_base = base
    while True:
        virtual_base *= base
        if virtual_base > argument and is_below:
            break
        elif virtual_base < argument and not is_below:
            break
        elif virtual_base == argument:
            return [exponent + 1, 0]
        exponent += 1
    return [
        exponent,
        (base**exponent) - argument if not is_below else argument - (base**exponent),
    ]


def index_rem(array: list[int]):
    return [x[1] % (x[0] + 1) for x in enumerate(array)]


def hole_xor(array: list[int]):
    counted = Counter(array)
    res: list[int] = []
    count = 0
    for el in sorted(set(array)):
        count += counted[el]
        res.append(count ^ el)
    return res


def base_possibilities(length: int, base: int = 2):
    """
    In case of base 2 and length 3. 2**3==8
    [0,0,0]
    [0,0,1]
    [0,1,0]
    [1,0,0]
    [0,1,1]
    [1,1,0]
    [1,0,1]
    [1,1,1]
    """
    return base**length
