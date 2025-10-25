"""
Mathematical Compressor

For breaking the entropy limit we must understand the next theory as a partial theorem (
hypothesis for now).

There is no such a thing like entropy instead what we got is interpretation that handle
poorly the data. Therefore chaos is just another expression of order.
"""

from argparse import Namespace
from typing import Any

# from math import log
from core.commands.compression.algorithms.kolmogorov.rome import krome

# from core.commands.compression.entropy.encoding import necessary_encoding
# from core.commands.compression.math.manipulation import ilog
# from core.commands.compression.math.decomposition import log_decomposition
# from core.commands.compression.math.relations import log_ratio, ratio
from core.commands.run import tcve_command
from core.context import Context
from core.io import OUT
from utils.args import ForgeParser


class CompressParser(ForgeParser):
    def setUp(self, *args: Any, **kwargs: Any) -> None:
        self.add_argument("value", nargs="+", type=str)


@tcve_command("compress", post_process=OUT.print, parser=CompressParser)
def compress(context: Context, value: list[str]):
    bvalue: bytes = " ".join(value).encode()
    numeric_value = int.from_bytes(bvalue)
    bit_length = numeric_value.bit_length()
    OUT.print(f"@-> Binary Length: {bit_length} bits")
    OUT.print(f"@-> Byte Length: {len(bvalue)} bytes")
    # base = 2
    # bits = log_decomposition(numeric_value, base=base)
    # We got so far 2 methods that give us a small value but different each time
    # 1. ratio or percentage value, give us a number from 0 to 1
    # 2. log, the logarithm of a number with base X, we can make it to be a number from 0 to 1 as well or perhaps we may want to use the base 2 dont know.
    # 3. We are going to use for the 3rd number the ... lets decide this TOMORROW so TODO
    # Actually we have that x/2**bit_len=p and log(x, 2)=l, this means that 2**l/2**bit_len=p or that log(2**bit_len*p, 2)=l
    # We could use all of those functions to retrieve the orignal x having in mind the loss of precision
    # ratio_part: float = ratio(numeric_value, base**numeric_value.bit_length())
    # log_part: float = log(numeric_value, base)
    # modular_part: float # TODO allow us to have the byte remainder of the numeric value for matching, once we got this modular value we need to
    # run all the possibilities and store the time taking to obtain the real value from the modular using the formula m*x+n=X

    return (
        numeric_value,
        krome(numeric_value),
        # value, bits, necessary_encoding(numeric_value),
        # ratio_part, log_part,
        # log_ratio(log_part=log_part, ratio_part=ratio_part, bit_length=bit_length, base=base)
    )
