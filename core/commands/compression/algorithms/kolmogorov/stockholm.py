from core.commands.compression.math.manipulation import ilog


def kholm(numeric_value: int, relation_top: int = 2**8):
    """
    Path Generator:

    Path Runner:

    """
    bit_length = numeric_value.bit_length()  # stop condition for generative algorithm
    max_pos_value = 2**bit_length
    remainder = numeric_value
    relation = (
        remainder * relation_top
    ) // max_pos_value  # a number from 0 to relation_top that tell us how filled is the recipient
    remainder = remainder - (relation * max_pos_value) // relation_top
    base = 1.001  # It advance to 0.001 percent each step
    exponent, remainder = ilog(base, remainder)
    remainder = int(base ** (exponent + 1) - base**exponent)
    return (bit_length, relation, exponent, remainder)
