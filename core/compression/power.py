"""
After watching RSA and understanding block cipher, we now want to compress a payload by:
Turning a block into a number that has an exact root (e.g. Square Root or x**1/2)
Let's say we have a file of one megabyte of size.
In order to use the same tools that RSA already uses, we can:
Obtain a 512 bytes integer
Create an 8 bytes structure with 2 integers of 4 bytes that will contain:
first 4 bytes: the number that is the root of the 512 integer for example 4294967296
second 4 bytes: the number that is the power of the root for example for an square root will be 2.

Considerations:
As the maximum value for a 4 bytes integer is 4294967296 (even though we could use an unsigned integer which is greater)
Once the root exceeds that number we should increase the power root for example if the square root is higher than the 2**32
then we should use the cubic root and repeat until we find a root that is equal or smaller than 2**32

The above algorithm must be recursive (using iterative approach please), which means once we obtain the roots and obtain a payload
compressed we must apply to the compressed payload the same algorithm until we reach a minimal payload size.

As it is possible the number doesn't have a root we must add another 4 byes to the compression layer to store the part that must be
taken away to make the number fit to have a root

B.E.R. Algorithm:
Given a number X, obtain 2 pair of numbers B and E such that |X-B**E|<<X where X-B**E=R and as such we want that R is much
more smaller than X in order of magnitude.
B stands for Base, and is a 4 bytes long unsigned integer
E stands for Exponent, and is a 2 bytes long unsigned integer
R stands for Remainder, and is a 4 bytes long unsigned integer
Exempli Gratia:
Given a number X=11
B could be 3
E could be 2
R would be then 2
as 2**3=9 and X=11 then 11-9=2 or R=2
Exempli Gratia #2:
Given a number X=1_000_003
B could be 10
E could be 6
R could be 3
....

Pseudo Algorithm:
Giving a number X
Finding E:
E < int(X**(1/2))


.... Update as it seems the powers of 2 give more smaller results or at least acceptable ones
for this reason we are going to avoid setting the base and focus instead on the exponent.
This way we save 4 bytes per block.
Now we are going to use the following algorithm given this random X=2315169600
2**31 give us a remainder of R=167685952
Applying the same logic to R we obtain 2**27, and then a R-2**27=33468224 so we recursively apply the same algorithm
until the remainder is smaller than the block size (in this case was 2**16 or something like that)

Compress Payload Architecture:
hashed content (n bytes) An integrity hash perhaps with MD5 that tell us whether or not the decompressed payload is correct or not
b: Always 2 so is omitted in the payload content
e: Exponent a 2 bytes long (up to 65536) integer that stores the power part of the compression
r: The remainder of the compression

"""

from decimal import ROUND_UP, Context, Decimal, getcontext
from typing import Literal, Optional, TypedDict

import numpy as np
from prompt_toolkit import prompt
from sympy import randprime

from utils.tests import Testable


def broken_pigeonhole():
    """
    The idea behind this function is to break pigeon hole theorem by presenting a counterexample,
    exampli gratia:
    Can we represent a number like 25 by using only 15 convinations? for example we could say for each value from 1 to 25 is there
    a way to transform the value such that x=1 up to 25 into a smaller way?
    theoretically we could represent the maximum value (i.e. 25) with just two numbers 5 and 2 where this represents the value 25 as
    5**2
    Now does this applies to every number below? it does if we use a correction factor, for example 24 is 4**2+9 or 5**2-1, therefore
    we could say that we need in binary form to represent a number like 25 (or any number from 1 to 25) 3 numbers, 1 for the remainder
    and one for the base and another for the exponent.
    Let's analyze its storage cost
    25 is 2**4 meaning its worth 4 bits of storage or one nibble
    25 when decomposed it needs 1 bit for the sign of the remainder, 3 bits for the base and 3 bits for the exponent meaning
    we are expanding the payload into 7 bits adding 3 bits to storage.
    If we used 25 as a composition of base 2 and exponent x, we noticed that 25 is 2**5-7, if the algorithm assumes that the base is
    always 2 and the operation is always substraction then we need 3 bits for the exponent and 3 bits for the remainders meaning
    a expantion of 1 bit.
    Still so far we have nothing now lets represents 25 as 2**5-(7)
    Turning 7 into a base of 2 it would be.
    2**5-(2**3-2**0) meaning we have 5 bits activated 5, 3, 0 or 1 0 1 0 1 this would be 25 at this point the transformation would need
    5 bits the same as the original value, therefore we aren't yet compressing.

    The idea is to break the payload without relying in entropy, we can notice above that 10101 is the same as using two sine functions
    with just two bits marked with 0 and 1
    first function sin(x) with arguments perhaps 1 indicating the number to match the function and describing where does the function
    contains its 1s.... the rest are just 0s.
    Above we are using the entropy in a binary level to compress the payload into a single bit.
    As per other theorems states we are just using low entropy because the generated number allows it.
    Lets also notice that 10101 is not actually 25, but instead is 2**4+2**2+2**0 it would be 16+4+1 or 21, maybe my error?
    indeed the actual number is 1 0 1 0 0 1 which is 6 bits long still greater than the actual original number and entropy no so friendly.
    lets use another approach.
    25=2**4+9 which is 2**4+2**3+2**0.
    25=11001 now this number is the actual 25, also again no entropy friendly.
    Lets try something different, when using base 2 we arent doing anything different than actually representing it in binary.
    lets break 25 into base 3.
    25=3**3-(2)
    Above we can notice that we need 2 something like.
    1 0 0 0
    and a later pre know fact to use the remainders as base of 2 in this case we need 2**1 which is 10
    therefore, the other thing we could do is:
    25 is 5**2, 5 is 3 bits long, while 2 is just 2**1 or 10 meaning 2 bits long still we are needing here 5 bits long to represent
    the number 25, this time
    10110
    This time we generated 16+4+2=22 this is how we turned 25 into an smaller number, lets retry this while following the next algorithm
    Square root of the input number + remainder.
    25==5 or 101 bits + 0 or 0 bits, now we can represent the number in 1010 bits with high entropy.
    Lets apply this algorithm as well for other stuff 27 is 5 and 2 meaning 10110 which means no reduction made on this algorithm.


    The problem that present pigeonhole theorem is:
    We can't represent a domain like one containing all natural positive numbers from 1 to 25 with an smaller domain like 1 to 5 without
    losing datal.
    Numerically speaking we can represent all Real numbers with a much smaller representation for example using logarithm,
    meaning for the domain D such that D contains all numbers natural or even Reals from 1 to 25 we can say that
    ln(d)=y where d is any number on the selected domain and y is a smaller representation.
    The problem y is as big as d in a computational context as we need to store the decimal part when dealing with floats.
    probably y is even bigger than d in a computer.
    What does the log of d means? we can represent any number with a much smaller representation, and being able to obtain the
    original number in a pristine way if we could successfully store all of the parts of the division. For example, we could index
    each particle of the universe as a 1 and taking the orders of those particles as their positions in the array at certain moment of
    time, and therefore generate a number from that binary array, we now could either wait until the numbers generated has an exact
    and relatively small logarithm or store the large logarithm, also we could reapply the logarithm to the previous logarithm and store
    the amount of iterations. The new number stored could be a new domain particles that is compressed into for example a bunker or
    similar, we now are able to restore the universe by reversing the previous operation.
    Why is the above impossible?
    If we want to represent 1000 objects we could just present 1 object as a sample and then proposing the audience to image 1000 objects
    of the kind, there is 1000 objects generated in each people imagination, isnt it?
    For example if I have 2 as a whole number and tell the people to imaginate the rest to obtain a movie payload, what would they do?
    try to guess, at least. but they dont have a function or algorithm to generate the movie payload. So imaginate all actors in the
    compression system like the movie example, what would we need?
    1. An input number
    2. A processor or transformer that transform the number into its original value
    3. The output value or perhaps a way to validate it (a hash perhaps?)

    Now lets watch some algorithms
    original_payload%(compression_domain**(1/2))
    The above for example for the 25 domain we could now say that there is we could use for the 23 number for example each of the values
    23%5=3
    then we know that 3 is only possible in 5 possibilities,3, 8, 13, 18, 23.
    Then working on the last possibility we could indicate this by using the number of the possibility in this case 5
    So 3 is at most 3 bits and 5 as well meaning 6 bits, (doesnt compress)
    For it to be a real math compression algorithm, we need to:
    1. use a unitary domain for representing numbers.
    As for the binary domain states that 0 is 0 and 1 is 1 but 10 is two and 11 is 3 then
    we need to be able to transform our interpretation of the binary domain into something cheaper.
    for example we could say that 10 (which is 2 in binary) means 10 in decimal. Instead of using 3 bits to represent a decimal factor
    we could say that ....
    """


class PFloatCorrector(TypedDict):
    pe: int
    pr: int


def ilog(base: int, argument: int):
    """
    Returns the logarithm of a number such that base**result=argument
    It also returns the remainder of the logarithm calculation
    """
    if base == argument:
        return 1, 0  # As base**1=argument
    elif argument == 0:
        raise ValueError("Cannot calculate this argument")
    elif base == 0 and argument != 0:
        raise ValueError("Cannot calculate this as 0**x is always 0")
    temporal_exponent = 2
    temporal_exponent_grow = 1
    temporal_result = None
    direction_grow = True
    while True:
        temporal_result = base**temporal_exponent
        if temporal_result < argument and direction_grow:
            temporal_exponent += temporal_exponent_grow
        elif temporal_result > argument:
            temporal_exponent -= temporal_exponent_grow
            direction_grow = False
        elif temporal_result < argument and not direction_grow:
            return temporal_exponent, argument - base**temporal_exponent
        if temporal_result == argument:
            return temporal_exponent, 0


def rlog(base: int, argument: int, acceptable_remainder: int = 1000):
    """
    Iteratives returns the logarithm in a way that the remainder is represented as the logarithm of the actual remainder and as such
    the remainder is smaller than the argument
    """
    log = ilog(base, argument)
    exponent_stack: list[int] = [log[0]]
    while True:
        log = ilog(base, log[1])
        exponent_stack.append(log[0])
        if log[1] < acceptable_remainder:
            break
    return exponent_stack


def decompose(value: int, exponent: int = 2):
    """
    Returns two factors for value that it can be represented using a notation of exponents, for example:
    decompose(16) = (2, 2), (2, 2), 0
    decompose(59) = (2, 2), (((2, 3,0), ( 2, 1)), 1), 1

    Step by step of decompose(59).
    1. Round it to an even number ~ 60
    2. 60-59=1 which is the last number 1 which is the correction to the original number
    3. Divide 60/2 which is 30 then we know 30*2 is 60, try again 30/2 is 15 so 15*4 is 60 then.
    4. Round 15 to its closest even number this is 16, then we got 16 and 4
    5. 16=8 * 2, 8 is 2**3 and 2 is 2**1 then
    """
    if not isinstance(value, int):  # type: ignore
        raise ValueError("You must provide us with an integer here")
    if value == 1:
        return (exponent, value, value, 0)  # This is the default factorization for 1
    elif exponent == 1 or exponent == 0 or value == 0:
        return (exponent, value, exponent, 0)  # This is a default return statement
    virtual_value = value  # Use this value for modifications and more leaving value intact so no modification is made over it
    eveness_correction = value % exponent
    is_even = eveness_correction == 0
    global_remainder = 0
    if not is_even:
        virtual_value = value + (exponent - eveness_correction)
        global_remainder = exponent - eveness_correction
    p1, p2 = virtual_value, 1
    while p1 % exponent == 0:
        p1 = (
            p1 // exponent
        )  # using floor division as we are looking for integers no floats
        p2 = p2 * exponent
        if p1 == p2:
            break  # A lot of reduction happened here
    return (exponent, p1, p2, global_remainder)


def iceil(a: int, b: int):
    """
    Do a ceil division using just integers
    """
    return -(-a // b)


def shrink(body: list[int]):
    shrinked_body: list[int] = [body[0], body[1]]
    for i in range(2, len(body), 2):
        for c in range(len(shrinked_body)):
            shrinked_body[c] += body[i]
        if i % 4 == 0:
            shrinked_body.append(body[i])
            shrinked_body.append(body[i + 1])
    print(f"Shrinked Length: {len(shrinked_body)}")
    print(f"Original Body Length: {len(body)}")
    return shrinked_body


def shred(value: int):
    """
    Composed by two members, headers and body.
    Headers are static and always present with the same size

    Headers
    =============
    1. 2b: Base Exponent, this leaves a remainder that will be then decomposed.
    2. 2b: Global remainder, this is the remainder left once we decompose the remainder completely.
    3. 2b: First factor of remainder decomposition.
    4. 2b: First correction of remainder decomposition

    Base Equation
    --------------
    The basic equation for this compression algorithm is:
    `X=Pb**H1+Gr`
    Where:
    * X is the decompressed payload
    * Pb is the Preshared Exponencial Base.
    * H1 is header 1 or base exponent
    * Gr is the global remainder, `NOTE: this is not the H2 as the H2 is the remainder of this remainder.`

    Now the Gr must be decomposed in order to obtain smaller components, for it we select two values that multiplied
    one by the other give a number close to the Gr value and store the remainder (difference) in a third component, the biggest
    part of the remainder is recursivelly decomposed until it fits inside 2 bytes of storage, this recursive decomposition is what
    we call the body of our compression algorithm.

    For finishing the header, we assign the first decomposition of Gr to the header (meaning H3 is the first remainder, and H4 the
    first correction) while we assign to the body the pairs for the recursive iterations.

    So in the equation the previous will looks like:

    `X=Pb**H1+(B*H3-H4)` # Where B is the body

    The body equation would look like below:
    `B=B'*B3-B4`
    * B': Means a recursive call the this same equation
    If we notice here, each new decomposition gots itself multiplied by the previous one and then the resulting correction stacks can
    be compressed into one.

    E.G.
    `X=Pb**H1+((((B'*B33-B43)*B32-B42)*B31-B41)*H3-H4)+H2`
    The above function is just needed for decompression and testing further compression now we have some entropy created should be done
    differently (perhaps using our previous sine algorithm?)
    Once the above function is shrinked meaning all components are in its more undreductable form (e.g. x**5-x**3-x**1-x**0) we proceed
    to convert the function to its binary representation, for example if 5, 3, 1, 0 we could say that 1 0 1 0 1 1 TODO

    The approximatelly payload size given all of the previous condition is:
    base for header: 4*2=8 bytes
    base for body: 0 bytes + binary convertion in worse case scenario 4096 for the first exponent and only one the algorithm inflates
    the payload by 8 bytes, but remember that if the case is that the payload is too close to the power of 2, no body would be needed
    and as such the reduction is far higher as would be 8 bytes against 512 bytes, therefore the worse case escenario cant happen.
    """
    base_exponent: int = 2
    e, r = ilog(base_exponent, value)  # This cover most of the number to shred apart
    initial_decomposition = decompose(
        r, base_exponent
    )  # Each decomposition costs us at least 2 bytes per part so rounding is 6 bytes so handle with care
    big_part = initial_decomposition[1]
    psf = None
    body: list[int] = []
    while (
        iceil(big_part.bit_length(), 8) > 2
    ):  # While it doesnt fit on a 2 byte length integer (Short integer)
        # decompose the previous big_part into big_part'*psf[1]-psf[2]
        psf = decompose(
            big_part, base_exponent
        )  # Each decomposition costs us at least 2 bytes per part so rounding is 6 bytes so handle with care
        big_part = psf[1]
        factor = ilog(base_exponent, psf[2])
        factor_remainder = ilog(base_exponent, psf[3])
        if factor[1] == 0:
            # Counter operation is 2**f0-fr0=input
            body.insert(0, factor[0])
        if factor_remainder[1] == 0:
            body.insert(1, factor_remainder[0])
        # body.insert(0, psf[2])
        # body.insert(1, psf[3])
    print(
        f"Estimated struct in bytes before compression: {iceil(value.bit_length(), 8)} bytes"
    )
    header: list[int] = [
        e,
        big_part,
        initial_decomposition[2],
        initial_decomposition[3],
    ]
    print("Shrinked body is: ", shrink(body))
    back_testing = _unshred(
        base=base_exponent,
        header=header,
        body=body,
    )
    assert (
        back_testing == value
    ), f"""Lossed data on decompression:\n{back_testing}\nis not\n{value}.\n
    Params: 
        Base: {base_exponent}
        Global Exponent: {header[0]}
        Global Remainder: {header[1]}
    """
    print(f"Estimated size of the payload is {len(header)*2} bytes for the header")
    print(f"Estimated size of the payload is {len(body)} bytes for the body")
    return [header, body]


def _unshred(base: int, header: list[int], body: list[int]):
    Gr = header[1]
    for i in range(0, len(body), 2):
        Gr = Gr * (base ** body[i]) - (base ** body[i + 1])
    Gr = Gr * header[2] - header[3]
    print("*" * 100)
    print(f"Base: {base}")
    print(f"Global Exponent: {header[0]}")
    print(f"Global Remainder: {header[1]}")
    print(f"Base Exponent: {base}")
    print("Partial Global Remainder is: %s" % Gr)
    print("Base Part is: %s" % base ** header[0])
    print("*" * 100)
    print("\n" * 3)
    return base ** header[0] + Gr


def unshred(value: int):
    """
    Uncompress or unshred a number into its original value
    Struct Protocol:
    Header
    -----------------------
    2 bytes: Base Exponent
    2 bytes: Remainder of the remainder decomposition, this part must be sum instead of operated like the others parts

    Body
    -----------------------
    2 bytes: Exponential components, this exponentials factors represent an exponential value that must be corrected
    2 bytes: Exponential correction, this regulates the factors into its correct original factor

    The decomposition happens
    """


def percent(part: Decimal | int, total: Decimal):
    return divmod((part * 100), total)


def unpercent(part: Decimal, percent: int):
    return divmod(part * 100, percent)


def ber_decompress(b: int, e: int, r: PFloatCorrector, block_size: int):
    float_correction = 100 - (r["pe"] + r["pr"])
    total = unpercent(b**e, r["pe"] + float_correction)
    return total.to_bytes(block_size, "big")


class BER(Testable):
    @classmethod
    def test(cls):
        if (
            prompt(
                "You want to input your own random number or wanna let us generate one for you? "
            ).lower()
            != "n"
        ):
            X = int(prompt("Enter your desire numeric data to compress below:\n"))
        else:
            X = randprime(2 ** (511 * 8), 2 ** (512 * 8))  # type: ignore
        compressed_payload = shred(X)  # type: ignore
        print(compressed_payload)


class BERCompressor:
    def __init__(
        self,
        payload: Optional[bytes] = None,
        base: int = 2,
        exponent: Optional[int] = None,
        remainders: Optional[PFloatCorrector] = None,
    ) -> None:
        self.block_size_bytes = 512
        self.block_size = 2 ** (self.block_size_bytes * 8)  # 512 bytes
        getcontext().prec = 512
        if payload:
            self.X = Decimal(int.from_bytes(payload, "big"))
        self.base = base
        self.e: Optional[int] = exponent
        self.r: Optional[PFloatCorrector] = remainders

    def compress(
        self,
    ):
        e, r = ilog(self.base, self.X)  # Calculates the logarithm with base 2
        pe = percent(self.base**e, self.X)
        pr = percent(r, self.X)
        # pe+pr should sum 100 this way we can correct the floating precision on decompression time
        # The correction algorithm works as follows
        # 1. We add up pe and pr which are parts of the remainder components
        # 2. We calculate 100-(pr+pe)
        # 3. The result of the above calculation is then added to either pe or pr for obtaining the total using the function unpercent, above
        # 4. With the above we have a way to correct floating precision errors
        # 5. The structure below which is the return of this function uses the following payload size:
        # 5.1. Base (b): 0 bytes or optionally 1 bytes as there is no real need to store the default base
        # 5.2. Exponent (e): 2 bytes as 65536 is enough for handling up to 1024 bytes long integers
        # 5.3. Remainder (percent exponent part, percent remainder part[pe, pr]): 16 bytes
        self.r = {"pe": round(pe), "pr": round(pr)}
        return (self.base, self.e, self.r)  # Stored space for R or Remainder

    def decompress(
        self,
    ):
        if self.e is None or self.r is None:
            raise ValueError(
                "Cannot decompress this payload, perhaps due to missing parameters? Try to compress it first"
            )
        return ber_decompress(self.base, self.e, self.r, self.block_size_bytes)
