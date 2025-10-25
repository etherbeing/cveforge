def number_generator(seed: int, bit_size: int, speed: int = 2):
    pattern = bin(seed)[2:]
    top = 2**bit_size
    bottom = 0
    number: int = top // 2  # Start from the middle of the data as a binary array
    for order in reversed(pattern):
        if order == "1":
            bottom = number
            number += (top - number) // speed
        elif order == "0":
            top = number
            number -= (number - bottom) // speed
    return number


def number_seed(number: int, speed: int = 2):
    seed = 0
    i = 0
    bit_size = number.bit_length()
    top = 2**bit_size
    bottom = 0
    while True:
        temp = (top + bottom) // speed
        if number > temp:
            seed += 2**i  # this is like adding a 0 at the end of the bit array :-)
            if bottom == temp:
                break  # to avoid infinite loop
            bottom = temp
        elif number < temp:
            if top == temp:
                break  # to avoid infinite loop
            top = temp
        else:
            break  # found
        i += 1
    return seed


def extreme_seed(value: int, wanted_bit_size: int = 4, speed: int = 2):
    print(f"@Value: {value}")
    result = value
    while result.bit_length() > wanted_bit_size:
        result = number_seed(result, speed=speed)

    print(
        f"@Back propagation: {number_generator(result, value.bit_length(), speed=speed)}"
    )
    return result


def krammstein(numeric_value: int):
    """
    How fast by using physics we could reach a certain threshold of value
    For example:
        for a random number X in the range of 2**511 to 2**512 if we want to make the threshold be 2**32 or something between those lines, we need to compute the time needed for under certain velocity we can reach
        a number or distance given...
    This would be treating the number of the payload as a distance, the problem is floating precision here as the raw time will depends on a division.
    Velocity=2**bit_length
    Distance=Input Payload Value (of size bit_length)
    Time=Compression Parameter
    V=D/T; T=D/V;

    """
    bit_length = numeric_value.bit_length()
    T = numeric_value / (2**bit_length)

    return T, bit_length, (numeric_value - int((2**bit_length) * T))
