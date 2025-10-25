"""
Play a  little with RSA
"""

import math
import sys
from decimal import Decimal, getcontext
from functools import lru_cache
from random import randint
from typing import Any, Optional, cast

import sympy as sp
import sympy.polys  # type: ignore[reportUnknownVariableType]
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from prompt_toolkit import PromptSession
from sympy import Symbol, integer_nthroot, isprime, powsimp, randprime, root

from utils.tests import Testable


class RSACracker:
    """
    A normal flow for RSA cracking would be:
    Obtaining the minimum starting possible number for the cracking algorithm, this is given by the next math formula.
    x**e and b*x-b+c
    Using the above formulas we can obtain all the numbers that have a natural root for e and also their remainder when divided by b
    is c.
    So for obtaining the last possible value we search for the last e in x**e where x is lower than n and that give us the highest 
    possible value for m**e which is x**e
    Now we determine the amount of possible values between the highest possible m and the lowest possible m by using the next formula:
    hp-lp=pv/n
    where hp is highest possible and lp is lowest possible and pv is possible values
    The meaning behind this is that after we know the range where we can find possible values for m which is barely:
    2**e up to (n-1)**e
    we can know how many times possibly fits n in m**e and what is the same
    (2**e+(n-1)**e)/n = pv
    because per each time that n fits in the range there is a remainder loop or what is the same we can again obtain the same remainder
    After testing this if the value of possible values is small then we go ahead and try to crack it but still the normal RSA values
    aren't that small so:
    Let's obtain the least possible significant number (lpsn) which is also most of the time the same as:
    activate the first bit of the integer for example if 4 bytes integer then:
    1000 0000
    0000 0000
    0000 0000
    0000 0000
    Then as we know the padding of the algorithm we assume first that most likely the number is in the range of
    2**(n_size-1) up to 2**(n_size)-1. Leaving at least a few possible numbers as an unknown value.
    We can just activate a bit in the 2**(n_size-1) and obtain its value, probably the actual m would be higher since we aren't 
    activating any more bit and that is something unlikely.
    Now testing the above with our test values:
    m**43%143=124 and m is 97
    for obtaining m we say:
    m is between the range of 0 to 143.
    m is between the range of 
    """
    def __init__(self, e: int, n: int, c: int):
        """
        e: is the public exponent usually 65537
        n: is the modulus of m**e
        c: is the cipher text encrypted with RSA
        """
        self.e = e
        self.n = n
        self.c = c

    def brute_force(self, from_value: int = 2, up_to: Optional[int]=None, key_size: Optional[int]=None, use_padding: bool=False, step: int=1):
        return rsa_brute_force(self.e, self.n, self.c, from_value=from_value, up_to=up_to, key_size=key_size, use_padding=use_padding, step=step)

def twin_breaker(n: int, c: int, e: int):
    """
    The twin breaker algorithm consist of two algorithm that advance at exponential speed by giving each other feedback,
    once the both twins functions agrees the payload can be considered as cracked.
    
    Benchmarks
    512 bytes key long
    """
    getcontext().prec = 124 # At the very least please
    
    def twin_b(m: int):
        x = (m**e-c)/Decimal(n)
        return x
    x = 1
    while True:
        m = (n*x+c)**Decimal(1/e)
        mi = int(m)
        if m != mi:
            x = twin_b(m=mi+1)
        else:
            break


def rsa_brute_force(
        e: int, n: int, c: int, from_value: int = 2, up_to: Optional[int]=None,
        key_size: Optional[int]=None, use_padding: bool=False,
        step: int=1
    ):
    # #0: Attempt to attack poorly padded payload with message equal to number 1
    if c == 1:
        print(f"#0 Cracked!!!! {int.to_bytes(c, length=key_size or 4)}")
        return 1
    # #1: Attempt to attack poorly padded payload with low length width, this works as for m**e%n=m**e for m**e smaller than n
    # this way we could just try c**(1/e) = m if m is an integer number, as this is too improbable to happen otherwise
    if 2**e < n: # means even the lowest possibility is safe from leaking
        m = c**(1/e)
        if m == int(m) and c%n==c: # it is an integer with no floating part
            print(f"#1 Cracked!!!! {int.to_bytes(m, length=key_size or 4)}")
            return m
    # #2: At this point we know that:
    # - m**e > n
    # - m**e % n == c
    # - m is not c
    # - if padded m is ensured to be no less than P (padded weakness)
    # pow((143*2+124), 43, 143)
    # The above the 124 or c, which is the cypher-text is modified by the 43 power or e because per each cycle there is an overflow of
    # (143*x + 124)*(143*(x-1)+124)%n.
    # The above means the normal function to crack the modulus which is hardened by the exponentiation is predictable once we
    # determine how the modulus function will overflow in a matplotlib graph we have that the y is similar to a sinus function
    # that ranges from 0 to n, where in this example n is 143, as per the c is not 0 the x axis doesn't start in the 0 but instead from
    # 124.
    # For the given problem we need to determine what a cycle is and per each value of the exponent determine how many cycles are there.
    # The cyclic function is given by the inverse of the path function let's denominate each:
    # 1. Path function: 143*x+124 or n*x+c
    # 2. Cyclic Function: (x-124)/143 or (x-c)/n
    # Now both the above function are linear or of inverse proportionality but the wanted function is still an exponential one at the very least
    # the exponential part is ...
    # Going on with the simplification let's resolve the cyclic function with a simpler terms like e=2,n=7,c=5
    step = max(step, 1) # ensure step is at least 1 to avoid infinite loop and busy wait
    pvs: set[int] = set()
    if key_size and use_padding:
        from_value = max((1 << (key_size-1)) | 1, from_value) # If we are giving a key size and we are using padding the number possibly starts at this point
    
    up_to = min(up_to, n) if up_to else n
    existences, remainder = divmod((up_to - from_value), c)
    if remainder:
        existences += 1

    # Quick adjust from value as m**e is higher than n
    # print("Looking for a suitable starting point")
    # from_value = randint(from_value, n//2)
    print(f"""
Stats:
    Range iterates from {from_value} up to {up_to} integer.
    
    Speeding iterations by applying math formula n*x+c for obtaining numbers
    that given a modulus n the remainders are c...
        There is at most {existences} possible values
        Using the steps we are going to iterate only on {round((up_to - from_value)/step)} possibilities
""")
    session: PromptSession[None] = PromptSession()
    session.prompt("Please input enter to go ahead...")
    x = from_value
    i = 0
    while True:
        # the step must be configured to become only possible values for example
        # let's say we want to obtain a linear function that given an index it returns a next possible value for x
        # x**e and b*x+c are the both conditions that must fulfill our next value meaning the value have a natural
        # root for e and is divisible by b which remainder is c... Even though our previous function just give us back
        # the states by separate, so we need to somehow determine the relation between the growth rate of the numbers
        # [(143*x+3)**43%143 for x in range(10)] 
        # The above function is right and is split in the way
        # ((n*x + U)**e)%n == c
        # The above is the truth function for cracking RSA but still needs the U factor which is the most important
        # The U factor is a number that may or may be not the m, as it can be the start of the series
        # then all we need is a function for the U factor as the real function that give us all the needed values is
        # (n*x + U)**e
        # 
        x = n*i+c
        if x%n==c:
            print(x**(1/e))
            pvs.add(x)
        i+= 1
        ## Lets advance the cursor for the next possible value this is the most important part as it help us to avoid large times when
        # dealing with non standard integers calculations
        # Normal advance is on the form x+=1 for a single byte encrypted payload this could end in a very low time (a few milliseconds)
        # But for a large encrypted payload which is the usual the cracking time is going to increase considerably.
        # So we need two things, avoid processing unnecessary numbers and quit as fast as possible.
        # For starting we could assume payload content so we have an starting point more realistic than the standard 2. This could work
        # for padded payload but for demonstration purposes we haven't been able to apply this to non padded purposes yet.
        # The second way is to increase the stepping of the iterations, there are two way for doing so, deterministically or random.
        # The first way is the preferred as it give us a more realistic time for cracking than the second. For cracking deterministically
        # we need to have two things into considerations, first if we are going to use exponential stepping or lineal stepping, 
        # the linear stepping takes a lot of time as the nature of the algorithm is exponential and the linear stepping algorithm is 
        # going to check a lot of possibilities that aren't needed. So for the purpose of speeding up the cracking purpose we need
        # to obtain the exponential factor for increasing the stepping this will close to the result as fast as possible using as well
        # the public exponent used in RSA.
        # For example for the numbers
        # 97**43%143=124
        # We need to find the first number that powered to 43 and mod by 143 its result is 124
        # For lineal function that give us those numbers that their power n is dividable by x we use
        # x**e = y
        # n*x+c = y
        # The first function give us the power e of a number without guarantee that the number is divisible by n
        # The second function give us the number y that is divisible by n without guarantee that the number have a root
        # Now we need a combination of both for obtaining all the numbers that
        # x**e - n*x
        # -46 is an special number for the series of m**43%n=c: NOTE
        if x > up_to:
            break
    if not pvs and key_size and use_padding:
        print(" No possible value obtained perhaps due to value being below too many zeroes?")
    print(f"Sorted possible values are: {sorted(pvs)}")
    return sorted(pvs)

# The next obtain the patterns in the step matching
# sorted(set(list([(rsa_brute_force(43, 143, 124, step=x) and x) or 0 for x in range(1, 1000)])))[1:]

class PythonInteractiveExtender:
    def __init__(self, command: str):
        self.command = command

    def __repr__(self) -> str:
        import os

        os.system(self.command)
        return f"{self.command} executed in underlying system"


clear = PythonInteractiveExtender("cls")


def print_pattern(exp: int, range_max: int = 9, depth: int = 5):
    values = [x**exp for x in range(1, range_max)]
    differences = [values[i] - values[i - 1] for i in range(1, len(values))]
    patterns = [differences[i] - differences[i - 1] for i in range(1, len(differences))]
    keep_digging: list[int] = [
        patterns[i] - patterns[i - 1] for i in range(1, len(patterns))
    ]
    print("----------------")
    print(values)
    print(differences)
    print(patterns)
    print(keep_digging)
    for _ in range(depth):
        if len(set(keep_digging)) == 1:
            print("Pattern found 🥳!!!")
            break
        if len(keep_digging) == 0:
            break
        keep_digging = [
            keep_digging[i] - keep_digging[i - 1] for i in range(1, len(keep_digging))
        ]
        print(keep_digging)
    print("----------------")


def print_table(
    rows: int,
    modulus: int,
    amount: int = 100,
    print_rows: bool = False,
    print_summary: bool = True,
):
    """
    Allows us to play with RSA operations
    """
    t: list[set[int]] = []
    for row in range(1, rows + 1):
        tt = set([(row**x) % modulus for x in range(amount)])
        if tt not in t:
            t.append(tt)
        if print_rows:
            print(tt)
    if print_summary:
        print("-" * 200)
        for i in t:
            print(i)
        print(f"Rows:{len(t)}")
        print("-" * 200)


def print_walkapath(
    power_dividend: int = 3, divisor: int = 4, maximum: int = 256
) -> dict[str, Any]:
    max_possible_existing: int = maximum // divisor + (1 if maximum % divisor else 0)
    _mpe = max_possible_existing ** (1 / power_dividend)
    max_possible_existing = round(_mpe)  # meaning we just need this amount of x in the
    if _mpe > max_possible_existing:
        max_possible_existing += 1
    print(
        f"Maximum possible existing are: {max_possible_existing} for power dividend: {power_dividend}, divisor: {divisor} and maximum: {maximum}"
    )
    # dividend to reach maximum or what is the same
    # x**e%n=c where x is just max_possible_existing steps....
    # Lets break it down now so it can be understood
    # for example given the equation 10**3%4=2
    # We now can say with this function formula that if traducing the equation to
    # x**3%4=2
    # and assuming for example whether max integer possible values or for example 256 (or byte maximum values)
    # we can say
    # 256//4=64
    # 64**(1/3)~4
    # So what the previous max_possible_existing values for x is 4 so now lets test it down
    v: dict[int, int] = {}
    for x in range(maximum):
        t = x**power_dividend
        if t >= maximum:
            break
        actual_value = t % divisor
        v[actual_value] = v.get(actual_value, 0) + 1
    print(v)
    total_count = sum(v.values())
    max_allowed = len(v.keys()) * max_possible_existing
    assert (
        total_count <= max_allowed
    ), f"Theory is wrong, because {total_count} is higher than {max_allowed}"
    print(
        f"The max actual repetitions obtained is {total_count} and the expected max is {max_allowed}"
    )
    return {
        "total_count": total_count,
        "max_allowed": max_allowed,
        "is_perfect": total_count == max_allowed,
    }


def crack_x(b: int, c: int, e: int, length: int = 10**3):
    """
    b = 5
    e = 3
    c = 2
    sorted(set([(x**e) for x in range(1, length)]) & set([b*x-b+c for x in range(1, length)]))
    [27, 512, 2197]
    Homologue: [(b*x-c)**e for x in range(1, 10)]
    Returns: [27, 512, 2197, 5832, 12167, 21952, 35937, 54872, 79507]

    ------
    [(b*x-b+c)**e for x in range(1, 10)]
    [64, 729, 2744, 6859, 13824, 24389, 39304, 59319, 85184]
    b = 5
    e = 3
    c = 4
    -----

    ---
    It seems that:
    b * x + c is enough the **e makes the others parts needed
    """
    assert (
        b > c
    ), "B is the quotient while c is the remained the modular division ensures that b is higher than c, so there must be something wrong (i can feel it a feeling I got, like something is about to happens if that means what I think it means we are in trouble big troubles I don't mean bananas as he says we are not taking any chances ... slim shady signature goes here xD)"
    return sorted(
        set([(x**e) for x in range(1, length)])
        & set([b * x - b + c for x in range(1, length)])
    )


def slim_shady(n: int, c: int, e: int):
    return [(n * x - n + c) ** e for x in range(1, 100)]


def ruffini_method(poly: sp.Symbol):
    x = sp.Symbol("x")
    """
    Reduce a polynomial to a quadratic or lower using synthetic division repeatedly.
    """
    factors = []  # To store linear factors
    poly = sp.Poly(poly, x)  # Ensure the polynomial is in proper format
    while poly.degree() > 2:  # Keep reducing until the degree is 2 or lower
        # Find possible rational roots (based on the Rational Root Theorem)
        coeffs = poly.all_coeffs()
        constant_term = coeffs[-1]
        leading_coefficient = coeffs[0]
        possible_roots = sp.divisors(constant_term) + [-d for d in sp.divisors(constant_term)]
        for root in possible_roots:
            # Check if the root is valid
            if poly.eval(root) == 0:
                factors.append(x - root)  # Add the linear factor
                # Perform synthetic division
                poly = sp.div(poly, x - root)[0]
                break
        else:
            # If no root is found, we stop (this shouldn't happen for reducible polynomials)
            break
    # The remaining polynomial is the quadratic (or lower-degree polynomial)
    return factors, poly.as_expr()


def kali_crack(x: int, n: int, c: int, e: int):
    """
    Test subject: [(b*x-b+c)**e for x in range(1, 10)]
    Test Result:
    [1040237395025459766629446506629158329354780004797445058162040169547269017412143295573786624, 218768222760923473684940018220552075023996521437630066272015628049270162435728532747310587753069585175763, 22372052970935888698372241240593850563122799640017353214605569000705210000000000000000000000000000000000000000000, 8653277796325383924685664585904379303866508122804747726276632767824760663355661298200128668679226477030760127356217977, 170685765117279622431386120883861769687034909185275233308149709283920113371986677573945101382612141401682228198040022286336, 526943820199707435635982131223009873734441377868091367046415173869220417272975076203936933936871316884089356416003313436543319, 457924600115334980910457765847195252328873309964480224522059071425614124138593525467834446731239650877563086441855925819610759168, 158328269575151877671371889856473763236580675679968463899367735839116041121505736102915745840136185762503373553045094013214111328125, 27172393951621967428785446102740632175410911199478404375850690691897848902963254647068350455953108249643090078693412105499315726712832]
    """
    # Using Ruffini's method we can determine all the possible x that satisfies the equation given meaning the possible M or decrypted messages

    return x**e - n * x + c


class RSA(Testable):
    """Tester class for RSA cryptography algorithm"""

    p: int = 0
    q: int = 0

    n: int = 0
    ep: int = 0
    d: int = 0

    def __init__(self, p: int, q: int, block_size: int = 1024) -> None:
        self.p = p
        self.q = q
        self.block_size = block_size
        assert q != p, "For RSA to work p must not be equal to q, or so they say"
        self.gen_n()
        self.gen_euler_phi()
        self.gen_e()
        self.gen_gcd()
        self.gen_d()

    @lru_cache
    def gen_euler_phi(
        self,
    ):
        """Generates the phi coefficient for RSA"""
        self.ep = (self.p - 1) * (self.q - 1)
        return self.ep

    @lru_cache
    def gen_carmichael_totient(
        self,
    ):
        """Generates the carmichael coefficient for RSA"""
        return  # Not implemented yet

    @lru_cache
    def gen_e(self):
        """Generates the e coefficient for RSA"""
        self.e = 65537 # cast(int, randprime(1, self.gen_euler_phi()))
        return self.e

    @lru_cache
    def gen_n(
        self,
    ):
        """Generates the n coefficient for RSA"""
        self.n = self.p * self.q
        return self.n

    @lru_cache
    def gen_gcd(self):
        """
        Extended Euclidean Algorithm to calculate gcd and the modular inverse of p modulo q.
        p = e (public exponent)
        q = phi(n) (Euler's totient)
        """
        a = self.p
        b = self.q
        q = 1
        r = None
        i = 0  # Cycles number
        while True:
            _t = divmod(a, b)
            print(
                f"""
Euclidean Cycle iter #{i}
a={a}
b={b}
q={_t[0]}
r={_t[1]}
"""
            )
            if _t[1] == 0:
                break
            q = _t[0]
            r = _t[1]
            a = b
            b = r
            i += 1
        self.gcd = r
        # EEA: EA Backward
        # Operation made: gcd(a, b) = ax + by
        # self.gcd = self.p*x + self.q*y
        # self.gcd = self.p * x + self.q * y
        # self.gc
        return self.gcd

    @lru_cache
    def gen_d(
        self,
    ):
        """
        Compute the modular multiplicative inverse of e modulo φ(n).
        """
        phi = self.ep
        e = self.e
        x, y = 0, 1
        last_x, last_y = 1, 0
        while phi != 0:
            quotient = e // phi
            e, phi = phi, e % phi
            last_x, x = x, last_x - quotient * x
            last_y, y = y, last_y - quotient * y
        self.d = last_x % self.ep
        return self.d

    @classmethod
    def cracking(
        cls,
        e: int,
        n: int,
        encrypted_payload: bytes,
        block_size: int,
        is_block_cypher: bool = True,
        real_d: Optional[int] = None,  # DONT USE UNLESS FOR TESTING
        payload_length: Optional[int] = None,  # DONT USE UNLESS FOR TESTING
    ):
        m_range_start: int = 2  # for cracking RSA we use a cycle from 2 to 255
        decrypted_payload: bytes = b""
        if is_block_cypher:
            block: int = int.from_bytes(encrypted_payload, "big")
            print(f"Block size {block_size} bits")
            # sys.set_int_max_str_digits(4096**2)

            def cracking_guide(x: int, c: int):
                # X is the position while C is the cypher-text block
                return n * x - n + c  # In the writings bx - b+c

            def cracking_guide_inverse(p: int, c: int):
                return p + n + c  # In the writings p+b+c

            def determine_start(c: int):
                """
                Given the fact that the m range starts at 2 always, then we can say that the start possible value is
                2**e, which in our test case means 2**43=8796093022208
                From that point onward we need to verify if that number is dividable by n and it returns the encrypted byte
                by using the cracking_guide and the cracking_guide_inverse functions
                """
                first_possible_value = m_range_start**e
                return cracking_guide_inverse(p=first_possible_value, c=c)

            if block == 1:
                print("Encrypted 1? maybe this is an error")
                decrypted_payload = int.to_bytes(
                    1
                )  # as 1%N=1 as (p-1)*(q-1) is always greater than 1 in practice
                return decrypted_payload

            print(f"Block bit length {block_size}, byte length {block_size//8}")
            real_value = (
                (pow(block, real_d, n)).to_bytes(length=block_size // 8)
                if real_d
                else None
            )
            cracked = RSACracker(e, n, block).brute_force(key_size=block_size, use_padding=False, step=1) # 65537
            
            print(
                f"""
Cracked: {cracked}
Orignal: {real_value}
"""
            )
            # The real deal?: {int.to_bytes(int(root(k, real_d)))}
            # Now we need to solve the padding subject, theoretically the payload is decrypted at this point but the problem is
            # that the padding is still encoding the payload and so we cannot see the actual raw content
        else:
            # Byte Cypher is too easy to break :-) Below it does break the RSA byte cypher implementation
            m_range_end: int = 255  # for cracking RSA we use a cycle from 2 to 255
            for byte in encrypted_payload:
                if byte == 1:
                    decrypted_payload += int.to_bytes(
                        1
                    )  # as 1%N=1 as (p-1)*(q-1) is always greater than 1 in practice
                    continue  # go to decrypt the next byte
                for attempt in range(m_range_start, m_range_end):
                    # For speeding up what we can do is:
                    # 1. Trying to decrypt first ASCII text and numeric values and after that the rest of values
                    # 2. Try to obtain a possible first index by reversing the module function
                    if (attempt**e) % n == byte:
                        decrypted_payload += int.to_bytes(attempt)
                        break
                else:
                    # the loop didn't break as it didn't find the correct value attempting in another way
                    # Implementing block decryption
                    print("=" * 200)
                    print(
                        f"TODO yet, cannot decrypt byte {byte} in position {len(decrypted_payload)}"
                    )
                    print("=" * 200)
                    break
                    # start = determine_start(byte=byte)
                    # cracking_guide(x=start, byte=byte)

                    # # What we need
                    # # for the next bytes we are going to test all possible values

                    # for x in range(m_range_start, m_range_end):
                    #     raw_value: int = cracking_guide(byte=byte, x=x)
        return decrypted_payload

    @lru_cache
    def encrypt_message(self, m: int):
        """
        Encrypt the message using the public key (e, n).
        for example lets say:
        character "a" = byte 97
        then m = 97 which is b"a"
        then c = (97**e) % n
        where n and e is a public factor which is shared with the client for encryption
        """
        return pow(m, self.e, self.n)  # This is the same as (m**self.e)%self.n

    @lru_cache
    def decrypt_message(self, c: int):
        """
        Decrypt the ciphertext using the private key (d, n).
        """
        return pow(c, self.d, self.n)  # This is the same as (c**self.d)%self.n

    def encrypt(self, payload: bytes):
        print(f"Encrypted bytes are: {payload}")
        m = int.from_bytes(payload, "big")
        assert (
            m < self.n
        ), "Message must be smaller than N, please use higher p and q for this to be done"
        print(f"Encrypted m is {m}")
        c: int = self.encrypt_message(m)
        print(f"Encrypted message c is: {c}")
        return int.to_bytes(c, length=self.block_size)

    def decrypt(self, payload: bytes):
        m: int = self.decrypt_message(int.from_bytes(payload, "big"))
        print(f"Decrypted message number m is: {m}")
        return int.to_bytes(m, length=self.block_size)

    @classmethod
    def test(cls) -> None:
        console: PromptSession[str] = PromptSession()
        q: int = cast(int, randprime(2**50, 2**55))
        p: int = cast(int, randprime(2**50, 2**55))
        rsa_instance = cls(q=q, p=p, block_size=512)
        print(f"Generated ep: {rsa_instance.ep}")
        print(f"Generated e: {rsa_instance.e}")
        print(f"Generated n: {rsa_instance.n}")
        print(f"Generated gcd: {rsa_instance.gcd}")
        print(f"Generated d: {rsa_instance.d}")
        print(f"Public part is: {rsa_instance.e, rsa_instance.n}")
        print(f"Private part is: {rsa_instance.d, rsa_instance.n}")
        message = console.prompt("Please input message to encrypt: ").encode()
        encryped_message = rsa_instance.encrypt(message)
        print(f"Encrypted message is:\n{int.from_bytes(encryped_message)}")
        decrypted_message = rsa_instance.decrypt(encryped_message)
        print(f"Decrypted message is:\n: {decrypted_message}")
        print(
            f"""Attempting crack: {
            cls.cracking(rsa_instance.e, rsa_instance.n, encryped_message, rsa_instance.block_size, real_d=rsa_instance.d)
        }"""
        )
        return
        print("*" * 200)
        print("Cracking now secure RSA implementations")
        print("Generating RSA key pair")
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048
        )  # 2048
        public_key = private_key.public_key()
        pd = padding.OAEP(
            mgf=padding.MGF1(
                algorithm=hashes.SHA256(),
            ),
            algorithm=hashes.SHA256(),
            label=None,
        )
        encrypted = public_key.encrypt(
            message,
            padding=pd,
        )
        print(f"Encrypted message: {encrypted}")
        secure_e = public_key.public_numbers().e
        secure_n = public_key.public_numbers().n
        print(f"Testing decryption: {private_key.decrypt(encrypted, padding=pd)}")
        print(f"Public key params e:{secure_e} n:{secure_n}")
        print(
            f"""Attempting crack: {
            cls.cracking(
                secure_e, secure_n, encrypted, block_size=public_key.key_size,
                real_d=private_key.private_numbers().d, # THIS is not necessary and should be removed to avoid conflicts or missunderstandings 
                payload_length=len(message)
            )
        }"""
        )
