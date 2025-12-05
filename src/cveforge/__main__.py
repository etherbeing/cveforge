#!/usr/bin/python
"""
Entrypoint and executable for CVE Forge
author: etherbeing
license: Apache
"""

import asyncio
import logging
import pathlib
import sys
from typing import Literal, NoReturn, Optional
from asgiref.sync import async_to_sync
from django.utils.translation import gettext as _
import typer

from cveforge.core.context import Context
from cveforge.utils.development import Watcher
from cveforge.utils.module import refresh_modules

from cveforge import entrypoint as entrypoint


async def program(context: Context, live_reload: bool):
    assert context.event_loop is not None, _(
        "Main event loop wasn't configured correctly"
    )
    context.get_commands.cache_clear()
    modules = refresh_modules(
        str(context.BASE_DIR.absolute()),
        exclude=[context.BASE_DIR / pathlib.Path("core/context.py")],
    )

    # Running the main process in a child process to be able to handle live reload and other IPC events
    watcher: Optional[Watcher] = None
    while True:
        try:
            elt_cui = context.event_loop.create_task(
                modules["cveforge.entrypoint"].main(context=context, modules=modules),
                name=context.ELT_CUI,
            )

            if live_reload and not watcher:
                watcher = Watcher(context=context)
                watcher.observer.name = "CVE Forge: File Observer"
                watcher.start(context.BASE_DIR)

            await elt_cui
            break
        except asyncio.CancelledError:
            continue


async def main(
    live_reload: bool,
    log_level: Literal["ERROR", "DEBUG", "INFO", "WARNING"],
    http_timeout: int,
    web_address: str,
    command: Optional[str],
    args: Optional[list[str]],
) -> NoReturn:
    event_loop = asyncio.get_running_loop()
    with Context() as context:
        context.set_event_loop(event_loop)
        assert context.event_loop is not None, _(
            "Main event loop wasn't configured correctly"
        )
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
            await context.event_loop.create_task(
                program(context, live_reload), name=context.ELT_PROGRAM
            )

            logging.debug("Child exit code, processed successfully exiting now...")
            context.stdout.print(
                "[green] 🚀💻 See you later, I hope you had happy hacking! 😄[/green]"
            )
            exit(context.RT_OK)


def cve_forge(
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
    return async_to_sync(main, force_new_loop=False)(
        live_reload=live_reload,
        log_level=log_level,
        http_timeout=http_timeout,
        web_address=web_address,
        command=command,
        args=args,
    )


def run():
    app: typer.Typer = typer.Typer(name="cveforge", invoke_without_command=True)
    app.command()(cve_forge)
    app(prog_name="cveforge", standalone_mode=False, args=sys.argv[1:])


if __name__ == "__main__":
    run()
