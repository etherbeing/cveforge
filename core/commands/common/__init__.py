"""
Common commands that are frequently used
"""
import logging
import os
import platform
from functools import lru_cache
from typing import Any

from rich.markdown import Markdown

from core.commands.run import tcve_command
from core.context import Context
from core.exceptions.ipc import ForgeException
from core.io import OUT
from utils.args import ForgeParser

logging.debug("Initializing common commands...")

@tcve_command('exit', )
def cli_exit(context: Context):
    """Exit the CLI"""
    raise ForgeException(code=context.EC_EXIT)

@lru_cache
def _get_help(context: Context):
    help = None # pylint: disable=redefined-builtin
    with open(context.ASSETS_DIR/"help.md", "r", encoding="utf8") as file:
        help = file.read()
    return Markdown(help)

@tcve_command('help', post_process=OUT.print)
def cli_help(context: Context):
    """Help command"""
    return _get_help(context)

@tcve_command('clear')
def clear(_: Context):
    """Clear command"""
    OUT.clear()

@tcve_command('restart')
def reload_process(context: Context):
    """
    Reload the current process by spawning a detached child process
    and terminating the current one.
    """
    raise ForgeException(code=context.EC_RELOAD)

@tcve_command('env', post_process=OUT.print)
def command_env(context: Context):
    """
    Return environment data for the current context that this Forge is running on
    """
    return f"""
{platform.platform()} {platform.machine()} {" ".join(platform.architecture())}
{platform.python_implementation()}: {" ".join(platform.python_build())} {platform.python_compiler()}

{"\n".join([f"{item[0]}={item[1]}" for item in os.environ.items()])}
"""

class log_parser(ForgeParser):
    def setUp(self, *args: Any, **kwargs: Any) -> None:
        self.add_argument(
            "--level", "-l", default=logging.DEBUG
        )
        self.add_argument(
            "message", nargs="+"
        )

@tcve_command(parser=log_parser, name="log")
def log(context: Context, message:str, level: str="DEBUG"):
    """
    Log the given message to the console as it would be logged to the file, this is useful for testing logging capabilities
    """
    int_level: int = logging.getLevelNamesMapping().get(level, logging.DEBUG)
    logging.basicConfig(
        filename=None,
        force=True
    )
    logging.log(level=int_level, msg=" ".join(message))
    OUT.print("[green]Printed given data into the configured output file[/green]")
    context.configure_logging()

@tcve_command(name="pwd", post_process=OUT.print)
def command_pwd(context: Context):
    return os.getcwd()

@tcve_command(name="ss", post_process=OUT.print)
def command_ss(context: Context):
    return "No sockets are active or command is not implemented yet"
