
def ilog(base: int, argument: int, is_below: bool=True) -> list[int]:
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
        raise ValueError('0 multiplied any times is going to return 0')
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
    return [exponent, (base**exponent)-argument if not is_below else argument-(base**exponent)]

def _restore(compress_payload: list[int], base: int=2, precision: int=16, remainder: int=0):
    compress_payload = compress_payload.copy() # Avoid reference manipulation
    exponent = compress_payload.pop(0)
    relatives = compress_payload
    big_part_payload = base**exponent
    payload = big_part_payload
    for relative in relatives:
        payload += relate_percents(relative, big_part_payload)
    return round(payload) + remainder

def relate_percents(percentage: float, value: int|float):
    """Returns the percentage of a value (its part)"""
    return (percentage*value)/100

def compress(payload: bytes):
    numeric_value: int= int.from_bytes(payload)
    base: int = 2
    precision: int = 16
    compressed_payload: list[int] = []
    exponent, remainder = ilog(base, numeric_value) # Step 1 we downgrade the complexity of the payload by representing most of its data into a power function
    reduced_payload = base**exponent
    assert remainder + reduced_payload == numeric_value, "This calculation is wrong Step #1, both remainder and reducer payload doesnt add the original numeric_value"
    compressed_payload.append(exponent) # We store this for later encoding
    # Step 2 Represent the remainder as a percentage of the base**exponent part
    encoded_remainder = (remainder*100)//reduced_payload
    assert relate_percents(encoded_remainder, reduced_payload) == (encoded_remainder*reduced_payload)/100, "This calculation is wrong at Step #2.0"
    remainder = numeric_value - round(reduced_payload + relate_percents(encoded_remainder, reduced_payload))
    compressed_payload.append(encoded_remainder)
    scraps = []
    while remainder.bit_length() > 8:
        t, remainder = ilog(2**8), remainder)
        print(t)

    test_restore = _restore(compress_payload=compressed_payload, base=base, precision=precision, remainder=remainder)
    print(f"Attempting to compress @{numeric_value.bit_length()} into ~@{sum([x.bit_length() for x in compressed_payload]) + remainder.bit_length()} bits?")
    
    assert test_restore == numeric_value, f"Cannot successfully decompress because {test_restore} is not {numeric_value}"

