def recursive_step(length: int = 5):
    a = 2
    b = 3
    yield a
    yield b
    for _ in range(length - 2):  # Minus 2 because a and b is already yielded
        a = a + b
        b = a - b
        yield a


class PrimeGenerator:
    primes = sorted([2, 3, 5, 7, 11])  # 5 first primes

    def __init__(self, length: int = 1) -> None:
        self.length = length

    def gen_prime(
        self,
    ):
        for x in range(self.length):
            if x < len(self.primes):
                yield self.primes[x]
            else:

                yield (self.primes[0] * x - (x - (x - 1)))  # Which is 2
