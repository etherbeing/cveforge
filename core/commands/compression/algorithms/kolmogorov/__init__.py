"""
# Kolmogorov Complexity Path Based Generative Algorithms
Algorithms based on Kolmogorv complexity instead of classical Shannon Entropy complexity

What we are trying to accomplish here:
1. Skip Pigeonhole theorem issues by assuming all payloads are higher than at least 4 bytes.
2. Skip Shannon entropy limits by treating the whole payload as a single piece of data.
3. Represent the data as subset of steps needed to be taken to reach the goal, each substep must contain at least one byte or speed factor of bits lesser than the input given
4. Probably the algorithm will have a remainder, the remainder should be stackable (addable or something but the stack must be done in a lower order than the original payload to save space)
5. We need to assume context as much as possible so then would be possible for each given input to obtain the expected output.

## Analogy:
`Rome Traveller`: A traveller ask a person how he can go to Rome from its position, the person answer the traveller that he will give him just one place to go so he can know
where to go from there, as if the person give the traveller too much information then the traveller wont be able to remember all. Then the person tells the traveller go to point
A there you will have a signal telling you where to go from there, and if you follow the signalised path you'll eventually get into Rome.

What the analogy means for data theory:
Assume we treat the payload (Rome) as a goal, single identificable and reachable goal, for this we turn any payload into its decimal (because is human readable) representation.
Now we know that we need to reach number X instead of some structure like [23, 40, 10, 23] (array of bytes). The behaviour of a numeric value give us some advantages for the context.

`Advantages`:
1. The bit length of the numeric value is the stop condition for the map reader function or navigation function.
2. We could deterministically obtain the wanted number with any kind of mathematical function (beware of the floating errors for this)
3. We dont suffer from entropy or structure constraints.

Now once we got the numeric value from here onwards X, we should represent that value as a set of parameters for differents functions.

### Navigation Functions
These would be the functions that are going to give us the steps to reach the X.
First lets recap what data we are storing for now:
1. bit_length: Just a tiny number that give us how big is the length of the payload, if needed we could also use just the exponent part with the base on context being 2

Functions:
A number X is said to be for example 31 bit long (4 bytes) then the number X is between 2**30 and 2**31, the number then it could be represented as X-2**30 obtaining
a number in the range of 2**30, as this does have some binary implications (each activated bit will tell us the grade of the next bit size) we are moving from here
`2**(bit_length-1) up to 2**(bit_length)` # Range of important data
This give us the range of the data:
Now we can split the range of the data into parts, for example:
2**8 or 1 byte parts
The above is represented in the mathematical equation:
speed=(2**bl-2**(bl-1))/part_size
where part_size is 2**8 or 1 byte long and bl is bit_length of the original value.
The part_size = 2**8 is stored on context meaning it doesnt consume storage for the compressed payload.
now we have a speed big enough to tell us where in which range of the important data is the payload.
Once we obtain the range for example is on range R we now know in which range is the expected payload. (this is probably a big range)

So far we only are storing two piece of data: R (small number in the range of 1 byte) and bl (small as well).
The R value tell us that the value is on the range R up to R+1, please not we are using this approach as using exponential here results on obtaining the same as the bits of
the numeric value.


"""
