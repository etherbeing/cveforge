"""
For example:
17 is 32 bits long
16 up to 32
17 - 16 = 1
We store 1 and 32 which is 2**5 meaning, 1 and 5
When cracking back remember:
X-2**4-2**3-2**2-2**1=Y
X-2**4-2**3-2**2-2**1=1
X-24-4-2=1
X=30=1
2**0+2**1+2**2+2**3=15

27 is 32 bits long
16 up to 32 bits long
27 - 16 = 11
11 is 16 bits long
11 - 8 = 3
3 is 4 bits long
4 is 2**2, and the target is 2**5
(((X-2**4)-2**3)-2**2)=Y
X-16-8=Y
X-24=Y
X-24=Y
X=3+24
X=27

f(17)=17-16-8-4-2-1-0=17=-14

"""


def mystic(number: int):
    bit_length = number.bit_length()
    lebit_size = 2 ** (bit_length - 1)
    val: int = number - lebit_size
    lebits: list[int] = []
    while lebit_size > 4 and val > 0:
        lebits.append(val.bit_length())
        if val > 0:
            lebit_size = 2 ** (val.bit_length() - 1)
            val = val - lebit_size
        else:
            break
    return val, bit_length, lebits
