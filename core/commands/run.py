"""File to handle run the CVE Forge commands"""

import logging
from argparse import Namespace
from typing import (
    Any,
    Callable,
    Optional,
    Sequence,
)

from core.commands.command_types import TCVECommand
from core.commands.exploits import ExploitParser
from core.context import Context
from core.exceptions.ipc import ForgeException
from utils.args import ForgeParser


class tcve_command:
    def __init__(
        self,
        name: str,
        parser: type[ForgeParser] | None = None,
        auto_start: bool = False, # This is NOT been used at all
        categories: (
            list[str] | None
        ) = None,  # list of categories this command belongs to
        post_process: Optional[Callable[..., Any]] = None,
        decorated_method: Optional[Callable[..., Any]] = None,
        defaults: list[str] | None = None,
        aliases: list[str]|None=None,
        cleanup: Optional[Callable[..., Any]] = None,
        hidden: bool = False,
        run_once: bool = False, # run once at the startup of the application reloads and so are to be made some other way
    ) -> None:
        self._run_once = run_once
        self._cleanup = cleanup
        self._hidden = hidden
        self._aliases = aliases
        self._decorated_method: Optional[Callable[..., Any]] = decorated_method
        self._categories = categories
        self._namespace: Optional[Namespace] = None
        self._parser: Optional[ForgeParser] = None
        self._name = name
        self.post_process = post_process
        self._auto_start = auto_start
        self._defaults = defaults
        self._cached_result: Any = None
        if parser:
            self._parser = parser(prog=name, exit_on_error=False, add_help=True)
            if decorated_method:
                self._parser.description = decorated_method.__doc__ or None

    def get_parser(self):
        return self._parser

    def on_commands_ready(self, context: Context):
        """
        Auto executed after all command are loaded and all files are inspected for example for avoiding race conditions when exploits aren't created yet
        """
        if self._parser:
            self._parser.setUp()
        if self._auto_start and self._decorated_method: # self._decorated_method is expected to be always True at this point
            parsed_kwargs = {}
            if self._parser:
                self._namespace = self._parser.parse_args([])
                parsed_kwargs = dict(self._namespace._get_kwargs())
            self.run(context, **parsed_kwargs)
        


    def has_aliases(self):
        return self._aliases is not None

    def expand_aliases(self):
        alias_dict: dict[str, TCVECommand] = {}
        if self._aliases:
            for alias_name in self._aliases:
                alias_dict[alias_name] = {
                    "command": self,
                    "name": alias_name
                }
        return alias_dict

    @property
    def hidden(self):
        return self._hidden

    @property
    def name(
        self,
    ):
        return self._name

    def run(
        self,
        context: Context,
        *args: str,
        extra_args: Optional[Sequence[str]] = None,
        **kwargs: dict[Any, Any]
    ):
        extra_args = args or extra_args
        logging.debug(
            "Calling decorated function %s with %s args: %s extra: %s kwargs: %s",
            (context.command_context.get("current_command") or {}).get("name", self._name),
            self._decorated_method,
            args,
            extra_args,
            kwargs,
        )
        if self._cleanup and self._cached_result:
            self._cleanup(self._cached_result) # Run the cleanup function with the result of the previous call
        result = None
        if self._parser and self._decorated_method:
            self._namespace = self._parser.parse_args(extra_args or args)
            parsed_kwargs = dict(self._namespace._get_kwargs())
            result = self._decorated_method(context, **parsed_kwargs)
        elif self._decorated_method:
            result = self._decorated_method(context, *args, **kwargs)
        elif not self._decorated_method:
            raise ForgeException("No module was passed when decorating")
        if self.post_process:
            self.post_process(result)
        self._cached_result = result
        return result

    def __call__(
        self,
        decorated_method: Callable[..., Any] | None = None,
        *args: Any,
        **kwds: Any
    ) -> Any:
        if self._decorated_method:
            if self._cached_result and self._cleanup:
                self._cleanup(self._cached_result)
            self._cached_result = self._decorated_method(*args, **kwds)
            return self._cached_result
        if decorated_method and not isinstance(decorated_method, self.__class__):
            self._decorated_method = decorated_method
            self.__doc__ = decorated_method.__doc__ or (self._parser.description if self._parser else None)
            if self._parser:
                self._parser.description = self._parser.description or self._decorated_method.__doc__
        elif isinstance(decorated_method, self.__class__):
            return decorated_method
        elif not self._decorated_method:
            raise ValueError(
                "No method passed, please use this function as a decorator"
            )
        return self


class tcve_exploit:
    """
    An exploit is an specific type of command that runs under the exploit namespace the name here would be a parser added to the exploit namespace
    """

    def __init__(
        self,
        name: str,
        date: str,
        parser: type[ForgeParser] | None = None,
        categories: list[str] | None = None,
        post_process: Callable[..., Any] | None = None,
        decorated_method: Callable[..., Any] | None = None,
        aliases: list[str]|None=None,
        auto_start: bool = False, # This is NOT been used at all
    ) -> None:
        ExploitParser.register_exploit(name, parser, self)
        self._aliases = aliases
        self._auto_start = auto_start
        self._decorated_method: Optional[Callable[..., Any]] = decorated_method
        self._categories = categories
        self._namespace: Optional[Namespace] = None
        self._parser: Optional[ForgeParser] = None
        self._name = name
        self._date = date
        self.post_process = post_process

    @property
    def name(
        self,
    ):
        return self._name

    def run(
        self,
        context: Context,
        *args: str,
        extra_args: Optional[Sequence[str]] = None,
        **kwargs: dict[Any, Any]
    ):
        extra_args = args or extra_args
        logging.debug(
            "Calling decorated function %s for function %s args: %s extra: %s kwargs: %s",
            self._name,
            self._decorated_method,
            args,
            extra_args,
            kwargs,
        )
        result = None
        if self._parser and self._decorated_method:
            self._namespace = self._parser.parse_args(extra_args or args)
            parsed_kwargs = dict(self._namespace._get_kwargs())
            if parsed_kwargs["option"] == "run":
                pass  # handle run option
            elif parsed_kwargs["option"] == "search":
                pass  # handle search option
            del parsed_kwargs[
                "option"
            ]  # remove it from the parsed kwargs as the decorated method doesn't care about it
            command_name, command_args = list(parsed_kwargs.items())[
                0
            ]  # from the items the first one is expected to be the exploit been called
            command_parser = ExploitParser.get_exploit_parser(command_name)
            if command_parser:
                ps = command_parser()
                namespace = ps.parse_args(command_args[1:])
                result = self._decorated_method(
                    context, **dict(namespace._get_kwargs())
                )
            else:
                result = self._decorated_method(context)
        elif self._decorated_method:
            result = self._decorated_method(context, *args, **kwargs)
        elif not self._decorated_method:
            raise ForgeException("No module was passed when decorating")
        if self.post_process:
            self.post_process(result)
        return result

    def __call__(
        self,
        decorated_method: Callable[..., Any] | None = None,
        *args: Any,
        **kwds: Any
    ) -> Any:
        if self._decorated_method:
            return self._decorated_method(decorated_method, *args, **kwds)
        if decorated_method and not isinstance(decorated_method, self.__class__):
            self._decorated_method = decorated_method
            if self._parser:
                self._parser.description = self._decorated_method.__doc__
        elif isinstance(decorated_method, self.__class__):
            return decorated_method
        elif not self._decorated_method:
            raise ValueError(
                "No method passed, please use this function as a decorator"
            )
        return self
