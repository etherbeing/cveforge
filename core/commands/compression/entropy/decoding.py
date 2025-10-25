def delta_decoding(array: list[int]):
    delta_decoded: list[int] = [array[0]]
    index = 1
    while index < len(array):
        delta_decoded.append(array[index] + delta_decoded[index - 1])
        index += 1
    return delta_decoded
