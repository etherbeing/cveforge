from math import log
from typing import Any


def shanon_score(array: list[Any]):
    """Calculate how much can we compress the payload and how much entropy it have"""
    unique_elements = set(array)
    length = len(array)
    probabilities: dict[Any, float] = {}
    for element in unique_elements:
        probabilities[element] = array.count(element) / length
    return -sum(map(lambda pi: pi * log(pi, 2), probabilities.values()))
