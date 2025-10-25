def krome(numeric_value: int, _part_size: int = 2**8, _base: int = 2) -> list[int]:
    """
    Example Usage:
    ```py
    krome(int.from_bytes(randbytes(32)))
    ```
    This is encoding as well no reduction is done
    """
    bt = numeric_value.bit_length()
    print("@Compressing: %s, size: %s bytes" % (numeric_value, bt / 8))
    values: list[int] = []
    # step #1 reduce size to base meaning the closer to the base the faster the road
    number: int = numeric_value - _base ** (
        bt - 1
    )  # make number smaller with a context defined behaviour (no need to store how here this is just part of the interpretation)
    # step #2 retrieve the size of the based number
    nbt = number.bit_length()
    # step #3 calculate a speed or part size for finding the original number
    size = (_base**nbt) // _part_size
    if size <= 1:
        raise ValueError(
            "Please make sure the payload is at least 2 bytes long if not we are not compressing under the current context"
        )
    # step #4 tell us where the part the number can be found (from 0 to 256 or _part_size parts)
    range_index = number // size  # the number is between speed*R and speed*R+1
    while number > _part_size and range_index > 0:
        values.append(range_index)
        number = number - (range_index) * size
        size = ((range_index + 1) * size - range_index * size) // _part_size
        if size != 0:
            range_index = number // size
        else:
            break
        if values[-1] == range_index:
            break  # dont add that to avoid infinite loop
    values.append(number)
    return values


def unkrome(values: list[int], _part_size: int = 2**8, _base: int = 2):
    print("@Decompressing values: %s" % values)
    # bt: int = values.pop()
    # nbt: int = values.pop()
    # speed = (_base**nbt)//_part_size
    # range_nv =  _base**(bt-1), _base**bt
    # range_nbt_nv =  _base**(nbt-1), _base**nbt
    # for value in values:
    #     pass
    # return range_nbt_nv
