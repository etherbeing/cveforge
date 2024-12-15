
import argparse
import os
import difflib
from pathlib import Path
import platform
import socket
from typing import Any, Iterable, List
from prompt_toolkit import PromptSession
from prompt_toolkit.completion.base import CompleteEvent, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import OneStyleAndTextTuple
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from pygments.lexers.html import HtmlLexer
from core.context import Context
from core.io import OUT
from utils.graphic import get_banner
from utils.module import load_module

commands: dict[str, dict[str, Any]] = {
    "exit": {"path": "core.commands.common", "name": "cli_exit"},
    "help": {"path": "core.commands.common", "name": "cli_help"},
    "clear": {"path": "core.commands.common", "name": "clear"},
    "banner": {"path": "core.commands.graphic", "name": "banner"},
    "search": {"path": "core.commands.security.cve", "name": "search"},
    "init_db": {"path": "core.commands.database.initialize", "name": "init_db"},
    "restart": {"path": "core.commands.common", "name": "reload_process"},
    "open": {
        "path": "core.commands.common.file",
        "name": "command_open",
        "post-process": OUT.print
    },
    "ip": {
        "path": "core.commands.security.surveillance",
        "name": "public_ip",
        "post-process": OUT.print,
        "kwargs": {
            "--interface",
            "-i"
        }
    },
}

class CustomCompleter(NestedCompleter):
    "Handle more complex and custom completion"
    def _get_executables(self, for_command: str) -> list[Completion]:
        for_command = for_command.lower()
        path = os.getenv("PATH")
        if not path:
            return []
        executables: list[Completion] = []
        if platform.system() == "Windows":
            folders = path.split(";")
        else:
            folders = path.split(":")
        for folder in folders:
            try:
                files = os.listdir(folder)
            except OSError: # if the user has no permission or the fodler doesnt exist
                continue
            for file in files:
                if file.lower().startswith(for_command) and os.path.isfile(Path(folder) / file):
                    file = Path(folder)/file
                    if (
                        file.name.endswith(".exe") or
                        file.name.endswith(".ps3")
                    ):
                        executables.append(
                            Completion(
                                file.name.removesuffix(".exe").removesuffix(".ps3"), 
                                start_position=-len(for_command)
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

    def _get_args_completion(self, for_command: str):
        return None # TODO not implemented yet

    def get_completions(self, document: Document, complete_event: CompleteEvent) -> Iterable[Completion]:
        command = document.text.strip()
        if command.startswith("@"):
            completions = []
            command = command.removeprefix(Context.SYSTEM_COMMAND_TOKEN)
            completions = self._get_executables(command)
            return completions
        else:
            return super().get_completions(document, complete_event)

def main():
    """
    Handle prompt and CLI as well as other program executable behaviour.
    """
    completer: CustomCompleter = CustomCompleter.from_nested_dict(
        dict(
            map(lambda command: [command[0], command[1].get("kwargs", {})], commands.items())
        )
    ) # type: ignore

    style = Style.from_dict({
        '': "#ff0066",
        'username': '#884444',
        'at':       '#00aa00',
        'colon':    '#0000aa',
        'pound':    '#00aa00',
        'host':     '#00ffff bg:#444400',
        'path':     'ansicyan underline',
    })
    message: List[OneStyleAndTextTuple] = [
        ('class:username', os.getlogin()),
        ('class:at',       '@'),
        ('class:host',     socket.gethostname()),
        ('class:pound',    '# '),
    ]
    session = PromptSession[str](
        message,
        completer=completer,
        lexer=PygmentsLexer(HtmlLexer),
        style=style,
        history=FileHistory(str(Context().history_path)),
        auto_suggest=AutoSuggestFromHistory(),
        complete_in_thread=True
    )

    OUT.print(
        get_banner(),
        new_line_start=True,
        justify="center",
        no_wrap=True,
        width=OUT.width,
    )

    OUT.print(
        "\n\n 🔓🦖💻 Welcome to [green]CVE Forge[/green], type 'exit' to quit. 🚀🫡🪖\n"
    )

    # elevate_privileges(session)

    while True:
        try:
            command: str = session.prompt().strip()
            if not command:
                continue
            base = command.split(" ", maxsplit=1)
            args = None
            if len(base) > 1:
                args = base[1].split(" ")
            base = base[0]
            cve_command = commands.get(base.strip(), None)
            if not cve_command and base.startswith(Context.SYSTEM_COMMAND_TOKEN):  # defaults to CLI
                command = command.removeprefix(Context.SYSTEM_COMMAND_TOKEN)
                os.system(command)
            elif cve_command:
                method = load_module(cve_command.get("path"), cve_command.get("name"))
                # from the same file than the method
                if method:
                    Parser: type[argparse.ArgumentParser] = load_module(cve_command.get("path"), cve_command.get("name") + "_parser") # type: ignore Automatically obtain the kwargs parser \
                    if Parser:
                        parser = Parser(exit_on_error=False, add_help=False)
                        try:
                            namespace = parser.parse_args(args)
                        except Exception as ex: # pylint: disable=broad-exception-caught
                            OUT.print(f"[red]{ex}[/red]")
                            continue
                        result = method(namespace)
                    else:
                        result = method()
                    post_process = cve_command.get("post-process", None)
                    if post_process:
                        post_process(result)
            else:
                closest_matches = difflib.get_close_matches(base, commands.keys(), n=1)
                if closest_matches:
                    OUT.print(
                        f"⚠️ Unknown command given, perhaps you meant [yellow]{closest_matches[0]}[/yellow]?"
                    )
                else:
                    OUT.print("❗💥 Unknown command given, use help to know more...")

        except KeyboardInterrupt:
            OUT.print("❗ Use 'exit' to quit.")
        except EOFError:
            OUT.print(
                "[green] 🚀💻 See you later, I hope you had happy hacking! 😄[/green]"
            )
            break
        except SystemExit as ex:
            exit(ex.code)
        except:  # pylint: disable=bare-except
            OUT.print_exception()

