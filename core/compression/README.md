# Entropy Compression

## Goal

To compress high entropy payload like for example an array full of bytes that are all uniques.

## Payload Compression Goal

An algorithm that is able to compress:

1. bytes(range(0, 256))
2. An array of randomly distributed unique bytes.
3. An array of randomly distributed bytes

## Glossary

- PG: Payload Goal

## Brainstorming

As for the PG #1 there is a clear and visible pattern, making use of it is not that great as is hardly impossible to obtain such a
pattern in a real world context, therefore lets break down the characteristics of the byte array:

1. Numeric domain comes from 0 to 256
2. It is a vector.
3. If unique the sum of its components is equal to 32640. The rest is -31.
4. An order array could be replaced by a bit array describing the positions of the elements of array.
5. In case there is an unordered array (e.g. [3, 1, 20, 13]) we need to first sort it somehow and with some algorithm that the ordered
   array is reversable into the original one. Lets discuss this later on another subsection.

So far we know that most transformations are useless to our purpose, let's think about this:
`Is it possible to compress high entropy data?`
My guess is: it is, the why? every numeric value can be represented in a way such that:
representation_of_x is smaller than x, for example `log(x)<x` .This holds true for all Real numbers.
But in computation we got that the storage of a float which is mostly what is inside a log(x)'s result probably holds more data
than x itself.
For example lets assume a 64 bit long (8 bytes) integer. If we apply the log(x) to that number we will probably need to use the same
amount of bits than the original number, for an standard floating we use (8 bytes long).

- Lets dig into the next math property:
  If we create 3 functions that 3 have X as their results and all of its parameters way smaller than X, then we could recreate the value of X by using those functions as corrections.

So far we can say that:
We could compress almost any text string as long as we use the next approach:
A text string would contain mostly alphanumeric characters therefore we could use the reduce algorithm to reduce the value of those strings for example 32 (' ') up to 126('z') there are 94 possibility, fit for ascii values....
Determining what kind of content could exist within a file give us a range of numbers that could be used for reduction.
