"""
Given a number X we need to store it in a smaller size
Example 4 is 2
if we want to store the number X to fit within a range we could just say:
X%R=Y
To obtain the number X we can use the function:
M*x+N=Y
Which translated to our issue it means:
R*i+Y=X
There is N possibilities for the value that gave us the wanted remainder.
Then we got that X%R=Y and here Y is a number between 0 and R.
For obtaining the correct i here that tell us in which range is the correct value we need to use some constraints.
for example lets say that we use R (range) to be 256 (to fit one byte).
2392%R=88
One possible constraint is 12, meaning the original number is between 2**11 and 2**12

Lets try again:
for X=91231092310923012309
X%R=213
L=67 (X.bit_length())
meaning the number is between 2**66 and 2**67
We used here 15 bits to store 67 bits.

Still we need to know how to  obtain i without actually storing it to recompose the original value.

"""


def normalize(array: list[int]):
    new_arr: list[float] = []
    max_allowed_exponent = len(
        array
    )  # means we need the max exponent in the sorted list to be lesser than this value
    new_arr = sorted(array)
    return new_arr, max_allowed_exponent
