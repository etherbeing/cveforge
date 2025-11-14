"""Interface for ArgumentParsers"""

import sys
from abc import abstractmethod
from argparse import ArgumentParser
from typing import Any, Optional, Union
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cveforge.core.context import Context

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
        self._context: Union['Context', None] = None
        super().__init__(*args, **kwargs)

    def set_context(self, context: 'Context'):
        self._context = context

    def _print_message(self, message: str, *args: Any, **kwargs: dict[str, Any]): # type: ignore
        if message and self._context:
            self._context.stdout.print(message)

    def exit(self, status: int = 0, message: str | None = None):  # type: ignore
        """
        This override leaves the parser with no mean to quit the program by default
        """
        if message:
            self._print_message(message)
        if self._context:
            sys.exit(self._context.EC_CONTINUE)

    @abstractmethod
    def setUp(  # pylint: disable=invalid-name
        self,
    ) -> None:
        """Setup arguments and subparsers"""
        raise NotImplementedError(_("Implement this to populate the arguments"))

    def __getattribute__(self, name: str) -> Any:
        return super().__getattribute__(name)
