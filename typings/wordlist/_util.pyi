""".util
is a private module containing utility
used for the actual implementation of
the wordlist generator
"""
from typing import Any, Generator, OrderedDict

def char_range(
    starting_char: str, ending_char: str
) -> Generator[str, Any, None]:  # -> Generator[str, Any, None]:  # noqa: F821
    """
    Create a range generator for chars
    """
    ...

def parse_charset(charset: str) -> str:  # -> str:
    """
    Finds out whether there are intervals to expand and
    creates the charset
    """
    ...

def scan_pattern(string: str) -> OrderedDict[int, Any]:  # -> OrderedDict[int, Any]:
    """
    Scans the pattern in the form @@@a@@ returning an OrderedDict
    containing the position of the fixed characters.
    """
    ...
