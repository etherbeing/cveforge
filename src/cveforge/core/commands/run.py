"""File to handle run the CVE Forge commands"""

from datetime import datetime
from typing import (
    Any,
    Callable,
    Iterable,
    Literal,
    Optional,
    Self,
)

from django.utils.translation import gettext as _
import typer

from cveforge.core.commands.command_types import TCVECommand
from cveforge.core.context import Context


context = Context()

type CVEEvents = Literal["ready", "completed"]


class tcve_base:
    def __init__(
        self,
        callable: Optional[Callable[..., Any]] = None,
        name: Optional[str] = None,
        date: Optional[datetime] = None,
        related_softwares: Optional[Iterable[str]] = None,
        related_ports: Optional[list[int]] = None,
        categories: Optional[list[str]] = None,
        hidden: bool = False,
        aliases: Optional[Iterable[str]] = None,
        auto_start: bool = False,
    ) -> None:
        self._auto_start = auto_start
        self._name = name
        self._typer: Optional[typer.Typer] = None
        self._callable = callable
        self._hidden = hidden
        self._categories = categories
        self._related_ports = related_ports
        self._related_softwares = related_softwares
        self._date = date
        self._aliases = aliases
        self._events: dict[CVEEvents, list[Callable[..., Any]]] = {
            "ready": [],
            "completed": [],
        }
        self._subcommands: dict[str, typer.Typer] = {}

        if self._auto_start:
            self.register("ready", self.run)

    @property
    def cli(self):
        return self._typer

    @property
    def name(
        self,
    ):
        if self._name:
            return self._name
        elif self.method:
            return self.method.__name__
        else:
            return str()

    @property
    def method(
        self,
    ):
        return self._callable

    @property
    def hidden(self) -> bool:
        return self._hidden

    @property
    def aliases(self):
        alias_dict: dict[str, TCVECommand] = {}
        if self._aliases:
            for alias_name in self._aliases:
                alias_dict[alias_name] = {"command": self, "name": alias_name}
        return alias_dict

    @property
    def subcommands(self):
        return self._subcommands.copy()  # avoid rewriting

    @property
    def __name__(self):
        return self.name

    def run(self, *args: Any):
        if self.cli:
            self.cli(prog_name=self.name, standalone_mode=False, args=args)

    def _register(self, into_typer: typer.Typer):
        if not self._typer and self.method:
            self._typer = typer.Typer(invoke_without_command=True)
            self._typer.command()(self.method)
            into_typer.add_typer(
                self._typer, name=self.name, invoke_without_command=True
            )

    def __call__(self, callable: Callable[..., Any], *args: Any) -> Any:
        if not self._callable and context.cli:
            self._callable = callable
            self._register(context.cli)
        return self

    def on(self, event: CVEEvents, *args: Any):
        events = self._events.get(event, None)
        if events is None:
            raise ValueError(_("Invalid event name given"))

        for e in events:
            e(*args)

    def register(self, event: CVEEvents, callback: Callable[..., Any]):
        events = self._events.get(event, None)
        if events is None:
            raise ValueError(_("Given event name doesn't exist"))
        events.append(callback)

    def add_subcommand(self, name: str, node: typer.Typer):
        self._subcommands[name] = node

    def subcommand(self, name: str) -> Optional[typer.Typer]:
        return self._subcommands.get(name, None)


class tcve_command(tcve_base):
    pass


class tcve_exploit(tcve_base):
    """
    An exploit is an specific type of command that runs under the exploit namespace the name here would be a parser added to the exploit namespace
    """

    _exploits: dict[str, Self] = {}
    _exploit_command: Optional[tcve_command] = None

    def _register(self, into_typer: typer.Typer):
        if not self._typer and self.method:
            into_typer.command(name=self.name)(self.method)

    def __call__(self, callable: Callable[..., Any], *args: Any, **kwds: Any) -> Any:
        if (
            self._callable is None
            and self._exploit_command
            and self._exploit_command.cli
        ):
            self._callable = callable
            run_cli = self._exploit_command.subcommand("run")
            if run_cli:
                self._register(run_cli)
            else:
                pass  # TODO at least a warning
        return self

    @classmethod
    def set_exploit_command(cls, command: tcve_command):
        cls._exploit_command = command

    def __new__(cls, *args: Any, **kwargs: Any):
        name: Optional[str] = kwargs.get("name")
        if not name:
            raise ValueError(_("A name must be given"))

        registered = tcve_exploit._exploits.get(name, None)
        if registered:
            return registered
        else:
            new = super().__new__(cls)
            new.__init__(*args, **kwargs)
            tcve_exploit._exploits[name] = new
            if cls._exploit_command and cls._exploit_command.cli and new.method:
                cls._exploit_command.cli.command()(new.method)
            return tcve_exploit._exploits[name]


class tcve_option(tcve_base):
    """
    Handles subparsers for exploits and commands
    """

    def __init__(self, command: tcve_base, is_command: bool=False, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._command = command
        self._is_command = is_command

    def __call__(self, callable: Callable[..., Any], *args: Any, **kwds: Any) -> Any:
        if self._callable is None and self._command.cli:
            self._callable = callable
            self._typer = typer.Typer(name=self.name, invoke_without_command=True)
            if self._is_command:
                self._command.cli.command(name=self.name)(callable)
            else:
                self._command.cli.add_typer(self._typer, invoke_without_command=True)
            self._command.add_subcommand(self.name, self._typer)
        return self
