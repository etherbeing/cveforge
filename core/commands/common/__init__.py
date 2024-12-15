"""
Common commands that are frequently used
"""
import os
from pathlib import Path
import sys
import subprocess
from functools import lru_cache
from rich.markdown import Markdown
from core.context import Context
from core.io import OUT

def cli_exit():
    """Exit the CLI"""
    raise EOFError()

@lru_cache
def _get_help():
    help = None # pylint: disable=redefined-builtin
    with open(Context.ASSETS_DIR/"help.md", "r", encoding="utf8") as file:
        help = file.read()
    return Markdown(help)

def cli_help():
    OUT.print(_get_help())

def clear():
    OUT.clear()

def reload_process():
    """
    Reload the current process by spawning a detached child process
    and terminating the current one.
    """
    exit(Context.EC_RELOAD)
