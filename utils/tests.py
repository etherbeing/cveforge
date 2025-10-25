from abc import abstractmethod
from typing import Any, Self


class Testable:
    runners: dict[str, Self] = {}

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        instance = super().__new__(cls)
        return instance

    @classmethod
    @abstractmethod
    def test(
        cls,
    ) -> None:
        """
        Run an interactive input like in the console for making the user able to test the class that
        implement this
        """
