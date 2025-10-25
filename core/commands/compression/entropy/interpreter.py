def to_sorted_matrix(array: list[int]):
    "Useful to detect sequences on the data"
    res: list[list[int]] = []
    index = 0
    while index < len(array):
        tarr = [array[index]]
        for e in array[index + 1 :]:
            if e >= tarr[-1]:
                tarr.append(e)
                index += 1
            else:
                break
        res.append(tarr)
        index += 1
    return res
