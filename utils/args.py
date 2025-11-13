"""Interface for ArgumentParsers"""

import sys
from abc import abstractmethod
from argparse import ArgumentParser
from typing import Any, Optional

from .translation import gettext as _


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
        super().__init__(*args, **kwargs)

    def exit(self, status: int = 0, message: str | None = None):  # type: ignore
        """
        This override leaves the parser with no mean to quit the program by default
        """
        from core.context import Context

        if message:
            self._print_message(message, sys.stderr)
        sys.exit(Context().EC_CONTINUE)

    @abstractmethod
    def setUp(  # pylint: disable=invalid-name
        self,
    ) -> None:
        """Setup arguments and subparsers"""
        raise NotImplementedError(_("Implement this to populate the arguments"))

    def __getattribute__(self, name: str) -> Any:
        return super().__getattribute__(name)
