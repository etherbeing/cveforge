#!/usr/bin/python
"""
Entrypoint and executable for CVE Forge
author: etherbeing
license: Apache
"""

import logging
import pathlib
import sys
import threading
from time import sleep
from collections.abc import Callable
from typing import Literal, Optional

import typer

from cveforge.core.context import Context
from cveforge.utils.development import FileSystemEvent, Watcher
from cveforge.utils.module import refresh_modules

# trunk-ignore(ruff/F401)
import cveforge.entrypoint  # type: ignore  # noqa: F401


def live_reload_trap(
    live_reload_watcher: Watcher, child: threading.Thread
) -> Callable[..., None]:
    def _trap(event: FileSystemEvent):
        return live_reload_watcher.do_reload(event, child)

    return _trap


def main(
    live_reload: bool = typer.Option(default=False),
    log_level: Literal["ERROR", "DEBUG", "INFO", "WARNING"] = typer.Option(  # noqa: F821
        default="INFO",
    ),
    http_timeout: int = typer.Option(default=30),
    web_address: str = typer.Option(default="127.0.0.1:3780"),
    command: Optional[str] = typer.Argument(
        help="""
(Optional) CVE Forge command to run, e.g: \"ip\"; The example before does returns the \
public ip of the user and exit after that, this suppress the interactive behavior of \
the CVE Forge software and is mostly useful for when running quick commands.
            """,
        default=None,
    ),
    # trunk-ignore(ruff/B008)
    args: Optional[list[str]] = typer.Argument(default=None),
):
    with Context() as context:
        context.set_web_address(web_address)
        context.configure_logging(
            logging.getLevelNamesMapping().get(log_level, logging.INFO)
        )
        if command:
            logging.debug("Running command directly from the command line")
            local_commands, aliases = context.get_commands()
            available_commands = local_commands | aliases
            cve_command = available_commands.get(command)
            if cve_command:
                logging.debug("Running command %s with args %s", cve_command, args)
                command_method = cve_command.get("command")
                if not command_method:
                    raise DeprecationWarning(
                        f"{cve_command.get('name')} method wasn't loaded as you're using a deprecated feature"
                    )
                else:
                    context.command_context.update({"current_command": cve_command})
                    command_method.run(*(args or []))
                exit(context.RT_OK)
            else:
                context.stdout.print(
                    f"[red]Invalid command given, {args} is not recognized as an internal command of CVE Forge[/red]"
                )
                exit(context.RT_INVALID_COMMAND)
        else:
            watcher = None
            if live_reload:
                watcher = Watcher(context=context)
                watcher.observer.name = "CVE Forge File Observer"
                watcher.start(context.BASE_DIR)

            while True:
                context.get_commands.cache_clear()
                modules = refresh_modules(
                    str(context.BASE_DIR.absolute()),
                    exclude=[context.BASE_DIR / pathlib.Path("core/context.py")],
                )

                # Running the main process in a child process to be able to handle live reload and other IPC events
                worker_thread = threading.Thread(
                    target=modules["cveforge.entrypoint"].main,
                    name=context.SOFTWARE_NAME,
                    daemon=False,
                    kwargs={"context": context, "modules": modules},
                )
                worker_thread.start()
                if watcher:
                    watcher.live_reload = live_reload_trap(
                        live_reload_watcher=watcher, child=worker_thread
                    )  # type: ignore
                    worker_thread.join()

                    if context.exit_status == context.EC_EXIT:
                        break
                    else:
                        sleep(1.5)
                else:
                    worker_thread.join()
                    if context.exit_status == context.EC_RELOAD:
                        sleep(1.5)
                        continue
                    break

            if watcher:
                watcher.stop()

            logging.debug("Child exit code, processed successfully exiting now...")
            context.stdout.print(
                "[green] 🚀💻 See you later, I hope you had happy hacking! 😄[/green]"
            )
            exit(context.RT_OK)


def start_app():
    app: typer.Typer = typer.Typer(name="cveforge", invoke_without_command=True)
    app.command()(main)
    app(prog_name="cveforge", standalone_mode=True, args=sys.argv[1:])


if __name__ == "__main__":
    start_app()
