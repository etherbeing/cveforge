"""
Entrypoint of the software handle run logic and call the needed modules from here
"""

import difflib
from functools import reduce
import getpass
import logging
import os
import platform
import shlex
import socket
import subprocess
import sys
from multiprocessing.connection import Connection

# import subprocess
from pathlib import Path
from typing import Any, Callable, Iterable, List, Optional, Self, Tuple, cast

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import NestedCompleter, Completer
from prompt_toolkit.completion.base import CompleteEvent, Completion
from prompt_toolkit.completion.nested import NestedDict
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import OneStyleAndTextTuple, StyleAndTextTuples
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.mouse_events import MouseEvent
from pygments.lexers.html import HtmlLexer


from core.commands.command_types import TCVECommand
from core.context import Context
from core.exceptions.ipc import ForgeException
from core.io import OUT
from utils.graphic import get_banner


class CustomCompleter(NestedCompleter):
    """Handle more complex and custom completion"""

    def __init__(self, *args: Any, context: Context, **kwargs: Any):
        self.context = context
        super().__init__(*args, **kwargs)

    def get_actual_command(self, for_command: str):
        parts = for_command.split() or [""]
        command = self.context.get_commands()[0].get(parts[0], None)
        if not command:
            return 
        self.context.command_context.update({"current_command": command})
        return command

    @classmethod
    def from_nested_dict(cls, data: NestedDict, context: Context) -> Self: # type: ignore
        options: dict[str, Completer | None] = {}
        for key, value in data.items():
            if isinstance(value, Completer):
                options[key] = value
            elif isinstance(value, dict):
                options[key] = cls.from_nested_dict(value, context) # type: ignore
            elif isinstance(value, set):
                options[key] = cls.from_nested_dict({item: None for item in value}, context) # type: ignore
            else:
                assert value is None
                options[key] = None

        return cls(options, context=context)

    def _get_executables(self, for_command: str) -> Iterable[Completion]:
        for_command = for_command.lower()
        path = os.getenv("PATH")
        if not path:
            return []
        executables: list[Completion] = []
        if platform.system() == "Windows":
            folders: list[str] = path.split(";")
        else:
            folders = path.split(":")
        for folder in folders:
            try:
                files = os.listdir(folder)
            except (
                OSError,
                FileNotFoundError,
            ):  # if the user has no permission or the folder doesn't exist
                continue
            for file in files:
                if file.lower().startswith(for_command) and os.path.isfile(
                    Path(folder) / file
                ):
                    file = Path(folder) / file
                    if file.name.endswith(".exe") or file.name.endswith(".ps3"):
                        executables.append(
                            Completion(
                                file.name.removesuffix(".exe").removesuffix(".ps3"),
                                start_position=-len(for_command),
                            )
                        )
        # if platform.system() == "Windows": # TODO Retrieve it from the DB instead of using Redis
        #     executables.extend(
        #         [
        #             Completion(
        #                 f"powershell.exe -c {command.strip()}",
        #                 start_position=-len(for_command)
        #             ) for command in getoutput("powershell -c \"Get-Command | Select-Object -Property Name\"").split("\n") if command.lower().startswith(for_command)
        #         ]
        #     )
        return executables

    def _get_args_completion(self, for_command: str)-> Iterable[Completion]:
        current_command = self.get_actual_command(for_command)
        if not current_command:
            return []
        parser = current_command.get("command").get_parser()
        if parser:
            command_parts = for_command.split()
            last_part = command_parts[-1]
            new_one = for_command.endswith(" ") or current_command.get("name") == last_part
            action_names = reduce(lambda x, y: x+y, [list(action.option_strings or cast(list[str], action.choices) or []) for action in parser._actions])
            action_names = filter(lambda action_name: new_one or action_name.startswith(last_part) ,action_names)
            # logging.info(list(action_names))
            command_parts[-1] = "{action_name}"
            return [ # TODO make the completion to work recursively within the subparsers to auto complete everything
                Completion(text=" ".join(command_parts).format(action_name=action_name), start_position=-len(for_command) - 1, display=action_name ) for action_name in action_names
            ]
        else:
            return []

    def _get_path_completion(self, command: str) -> Iterable[Completion]:
        parts = command.split()
        if not parts:
            return []
        last_part = parts[-1]
        suggestions: Iterable[Completion] = []
        if last_part.startswith("/"):
            return []
        if len(parts) > 1:
            try:
                for suggestion in Path(os.getcwd()).glob(last_part + "*"):
                    relative_path = suggestion.relative_to(os.getcwd())
                    str_path = str(relative_path)
                    suggestions.append(
                        Completion(text=str_path, start_position=-len(last_part))
                    )
            except NotImplementedError:
                pass
        return suggestions

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        command = document.text.strip()
        if command.startswith(Context.SYSTEM_COMMAND_TOKEN):
            completions = []
            command = command.removeprefix(Context.SYSTEM_COMMAND_TOKEN)
            completions = self._get_executables(command)
        else:
            completions = super().get_completions(document, complete_event)

        return [*completions, *self._get_args_completion(command), *self._get_path_completion(command)]

class CustomLexer(PygmentsLexer):
    def __init__(self, *args: Any, context: Context, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._context = context
    
    def lex_document(self, document: Document) -> Callable[[int], List[Tuple[str, str] | Tuple[str, str, Callable[[MouseEvent], object]]]]:
        get_super_line = super().lex_document(document)
        def get_line(*args: Any, **kwargs:Any):
            super_styles = get_super_line(*args, **kwargs)
            styles: StyleAndTextTuples = []
            default_style = super_styles[0][0] if len(super_styles) > 0 and len(super_styles[0]) > 0 else ""
            parts = document.text.split() or [""]
            current_command = self._context.command_context.get('current_command')
            if current_command and parts[0] == current_command.get("name"):
                styles = [("class:command", parts[0])]
                remainder = document.text[len(parts[0]):] # use this way and not the parts array because we need to respect the blank spaces
                if len(remainder) > 0:
                    styles.append(cast(OneStyleAndTextTuple, (default_style, remainder)))
            else:
                styles = [(default_style, document.text)]
            return styles
        return get_line

def get_message(context: Context) -> List[OneStyleAndTextTuple]:
    """Obtain a beautiful prompt message declared here for auto-updating the CWD"""
    return [
        # The design is shamelessly copied from kali linux terminal and intended for personal use
        # Kali devs know how to make a real terminal 😎 Not even msfconsole have this amazing
        # terminal
        (
            "class:colon",
            """
┌──(\
""",
        ),
        ("", getpass.getuser()),
        ("class:at", "(-☠️ -)"),
        ("class:host", socket.gethostname()),
        (
            "class:colon",
            """\
)-[""",
        ),
        ("class:path", os.getcwd()),
        ("class:colon", "]"),
        (
            "class:colon",
            """
|──[ 🌐 """,
        ),
        ("class:title", f"Web UI: http://{context.web_address}"),
        ("class:colon", " ]"),
        (
            "class:colon",
            """
|──[ ✨ """,
        ),
        ("class:title", "cve_forge v1.0.0"),
        ("class:colon", " ]"),
        (
            "class:host",
            f"""{f" Proxy: << {context.proxy_client} >>" if context.proxy_client else ''}""",
        ),
        ("class:colon", "\n|" if context.command_context.get("remote_path") else ""),
        (
            "class:colon",
            f"──[{context.command_context.get("remote_path")}]" if context.command_context.get("remote_path") else "",
        ),
        (
            "class:colon",
            """
└─""",
        ),
        ("class:pound", "# "),
    ]


def main(pipe: Connection, context: Context) -> None:
    """
    Handle prompt and CLI as well as other program executable behavior.
    """
    OUT.clear()
    context.configure_logging()
    if (
        platform.system() == "Linux"
    ):  # A workaround to make it work doesn't actually know if is needed but without it doesn't work
        sys.stdin = os.fdopen(0)
        sys.stdout = os.fdopen(1, "w")
        sys.stderr = os.fdopen(2, "w")
    local_commands, local_aliases = context.get_commands()
    available_callables: dict[str, TCVECommand] = local_commands|local_aliases
    completer: CustomCompleter = CustomCompleter.from_nested_dict(
        data={
            command[0]: command[1].get("kwargs", {})
            for command in available_callables.items()
        },
        context=context,
    )

    style = Style.from_dict(
        {
            "": "#ff0066",
            "username": "#884444",
            "at": "#00aa00",
            "command": "#00aa00",
            "colon": "#0000aa",
            "pound": "#00aa00",
            "host": "#00ffff",
            "path": "ansicyan underline",
            "white": "white",
            "title": "white",
        }
    )
    session = PromptSession[str](
        get_message(context=context),
        completer=completer,
        lexer=CustomLexer(HtmlLexer, context=context),
        style=style,
        history=FileHistory(str(context.history_path)),
        auto_suggest=AutoSuggestFromHistory(),
        complete_in_thread=True,
    )
    context.set_console_session(session)

    OUT.print(
        get_banner(context=context),
        new_line_start=True,
        justify="center",
        no_wrap=True,
        width=OUT.width,
    )

    OUT.print(
        "\n\n 🔓 🦖 💻 Welcome to [green]CVE Forge[/green], type 'exit' to quit. 🚀 🫡 🪖\n"
    )

    while True:
        try:
            command: str = session.prompt(
                get_message(context=context), in_thread=True,
            ).strip()
            if not command:
                continue
            base = shlex.split(command)
            args = None
            if len(base) > 1:
                args = base[1:]
            base = base[0]
            cve_command: Optional[TCVECommand] = available_callables.get(base.strip(), None)
            if not cve_command and base.startswith(
                context.SYSTEM_COMMAND_TOKEN
            ):  # defaults to CLI
                command = command.removeprefix(context.SYSTEM_COMMAND_TOKEN)
                subprocess.run(
                    command,
                    shell=True,
                    check=False,
                    stdin=sys.stdin,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    preexec_fn=(
                        cast(Optional[Callable[..., Any]], os.setpgrp if platform.system() != "Windows" else None)  # type: ignore[attr-defined] # pylint: disable=no-member
                    ),
                )
            elif cve_command:
                try:
                    context.command_context.update({"current_command": cve_command})
                    command_method = cve_command.get("command")
                    if not command_method:
                        raise DeprecationWarning(f"Method {cve_command.get('name')} not loaded due to deprecated feature used")
                    else:
                        command_method.run(context, extra_args=args)
                except ForgeException as ex:
                    if ex.code == context.EC_EXIT or ex.code == context.EC_RELOAD:
                        raise ex
                    else:
                        OUT.print_exception()
                        continue
                except Exception as _:  # pylint: disable=W0718
                    OUT.print_exception()
                    continue
            else:
                closest_matches = difflib.get_close_matches(
                    base, available_callables.keys(), n=1
                )
                if closest_matches:
                    OUT.print(
                        f"""⚠️ Unknown command given, perhaps you meant [yellow]{
                        closest_matches[0]
                        }[/yellow]?
                    """
                    )
                else:
                    OUT.print(
                        f"❗💥 Unknown command given, use help to know more...\nOptions are:\n  {', '.join(available_callables.keys())}"
                    )
        except ForgeException as ex:
            pipe.send(ex)
            break
        # except block catch
        except (KeyboardInterrupt, EOFError):
            OUT.print("❗ Use 'exit' to quit.")
        except SystemExit as ex:
            logging.debug(
                "Catching exit attempt with code %s (DEPRECATED please move to ForgeException IPC)",
                ex,
            )
        except Exception:  # pylint: disable=bare-except
            OUT.print_exception()
