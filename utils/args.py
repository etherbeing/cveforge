"""Interface for ArgumentParsers"""

from abc import abstractmethod
from argparse import ArgumentParser
from gettext import gettext as _
from typing import Any, Optional


class ExceptionParser(Exception):
    status: int
    message: Optional[str]

    def __init__(
        self, status: int, *args: object, message: Optional[str] = None
    ) -> None:
        super().__init__(*args)
        self.status = status
        self.message = message


class ForgeParser(ArgumentParser):
    """Override this class for new parsers"""

    def __init__(self, *args: Any, **kwargs: Any):
        kwargs.setdefault("prog", "cve_forge")
        kwargs.setdefault("exit_on_error", False)
        self.exit_cleanly: bool = False
        super().__init__(*args, **kwargs)

    @abstractmethod
    def setUp(  # pylint: disable=invalid-name
        self,
    ) -> None:
        """Setup arguments and subparsers"""
        raise NotImplementedError("Implement this to populate the arguments")

    def __getattribute__(self, name: str) -> Any:
        return super().__getattribute__(name)
