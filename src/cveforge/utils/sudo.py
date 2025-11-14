import ctypes
import logging
import os
import platform
import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter

try:
    from multiprocessing.connection import Connection
except ImportError:
    from multiprocessing.connection import PipeConnection as Connection

from core.context import Context


def is_admin() -> bool:
    """
    Return whether or not this software is running as admin
    """
    if platform.system() == "Windows":
        try:
            # only windows users with admin privileges can read the C:\windows\temp
            os.listdir(
                os.sep.join([os.environ.get("SystemRoot", "C:\\Windows"), "temp"])
            )
            return True
        # trunk-ignore(ruff/E722)
        except:  # pylint:disable=bare-except  # noqa: E722
            return False
    else:  # assume is unix like
        return (
            os.geteuid() == 0  # type: ignore[attr-defined] # pylint:disable=no-member
        )  # effective user id is not root


def elevate_privileges(pipe: Connection, context: Context):
    if platform.system() == "Windows":
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
    else:
        os.execvp("sudo", ["sudo", "python3"] + sys.argv)


def prompt_elevate_privileges(session: PromptSession[str]):
    """
    Ensure the current running software is running as administrator this is os aware
    """
    if not is_admin():
        while True:
            context.stdout.print(
                """
This software requires administrator privileges as socket runs in raw mode, \
read more about it on google... Enter [yellow]\"continue\"[/yellow] to try to \
elevate privileges or [red]\"cancel\"[/red] to cancel the operation: \
"""
            )
            answer = session.prompt(
                completer=WordCompleter(
                    ["continue", "cancel", "exit"], ignore_case=True
                ),
            )
            if answer.lower() == "cancel" or answer.lower() == "exit":
                context.stdout.print("[red]Exiting now as you have not enough permission[/red]")
                exit(1)
            elif answer.lower() == "continue":
                pass
            else:
                continue
            logging.error("NOT IMPLEMENTED YET")
            return
            # elevate_privileges()
            # sys.exit()
