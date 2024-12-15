import ctypes
import os
import platform
import sys
# from rich.style import Style
# from rich.color import console
from prompt_toolkit import PromptSession
# from prompt_toolkit import ANSI
from prompt_toolkit.completion import WordCompleter

from core.io import OUT



def is_admin() -> bool:
    """
    Return whether or not this software is running as admin
    """
    if platform.system() == "Windows":
        try:
            # only windows users with admin privileges can read the C:\windows\temp
            os.listdir(os.sep.join([os.environ.get('SystemRoot','C:\\Windows'),'temp']))
            return True
        except:  # pylint:disable=bare-except
            return False
    else:  # assume is unix like
        return (
            os.geteuid() == 0  # type: ignore # pylint:disable=no-member
        )  # effective user id is not root


def elevate_privileges(session: PromptSession[str]):
    """
    Ensure the current running software is running as administrator this is os aware
    """
    if not is_admin():
        while True:
            OUT.print(
"""
This software requires administrator privileges as socket runs in raw mode, \
read more about it on google... Enter [yellow]\"continue\"[/yellow] to try to \
elevate privileges or [red]\"cancel\"[/red] to cancel the operation: \
"""
            )
            answer = session.prompt(
                completer=WordCompleter(["continue", "cancel", "exit"], ignore_case=True),
            )
            if answer.lower() == "cancel" or answer.lower() == "exit":
                OUT.print("[red]Exiting now as you have not enough permission[/red]")
                exit(1)
            elif answer.lower() == "continue":
                pass
            else:
                continue
            if platform.system() == "Windows":
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
            else:
                os.execvp("sudo", ["sudo", "python3"] + sys.argv)
            sys.exit()
