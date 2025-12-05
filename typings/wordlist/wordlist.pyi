"""Wordlist

Generates all possible permutations of a given charset.
"""

from typing import Generator as TypeGenerator
from typing import Any

class Generator:
    """
    Wordlist class is the wordlist itself, will do the job
    """

    def __init__(self, charset: str, delimiter: str = ...) -> None: ...
    def generate(
        self, minlen: int, maxlen: int
    ) -> TypeGenerator[str, Any, None]:  # -> Generator[str, Any, None]:
        """
        Generates words of different length without storing
        them into memory, enforced by itertools.product
        """
        ...

    def generate_with_pattern(
        self, pattern: str = ..., data: str = ..., composed: bool = ..., prev: str = ...
    ) -> TypeGenerator[str | Any, Any, None]:  # -> Generator[str | Any, Any, None]:
        """
        Iterative-Recursive algorithm that creates the list
        based on a given pattern
        Each recursive call will concatenate a piece of string
        to the composed parameter
        data contains the dict created by scanning the pattern
        composed contains the current composed word (works recursively)
        prev is the index of the previous data object used.
        """
        ...
