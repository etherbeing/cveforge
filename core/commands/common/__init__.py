"""
Common commands that are frequently used
"""
import logging
import os
import pathlib
import platform
import shutil
import stat
from functools import lru_cache
from typing import Any, TypedDict

from rich.markdown import Markdown

from core.commands.command_types import TCVECommand
from core.commands.run import tcve_command
from core.context import Context
from core.exceptions.ipc import ForgeException
from core.io import OUT
from utils.args import ForgeParser

logging.debug("Initializing common commands...")

@tcve_command('exit', )
def cli_exit(context: Context):
    """Exit the CLI"""
    if context.live_reload:
        context.live_reload = False
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

@tcve_command(name="install")
def install(context: Context):
    logging.info("Installing CVE Forge in the user session, system-wide installation is NOT supported yet")

    EXEC_PATH = pathlib.Path("~/.local/bin/cveforge").expanduser()
    DESKTOP_PATH = pathlib.Path("~/.local/share/applications/cveforge.desktop").expanduser()
    ICON_PATH = pathlib.Path("~/.local/share/icons/hicolor/256x256/apps/cveforge.png").expanduser()
    shutil.copy(context.ASSETS_DIR / ".install/cveforge.sh", EXEC_PATH)
    exec_content = None

    with open(EXEC_PATH, "r", encoding="utf-8") as file:
        exec_content = file.read()
    with open(EXEC_PATH, "w", encoding="utf-8") as file:
        file.write(exec_content.format(ABSOLUTE_PATH=context.BASE_DIR.absolute()))

    os.chmod(EXEC_PATH, EXEC_PATH.stat().st_mode | stat.S_IEXEC)

    shutil.copy(context.ASSETS_DIR / ".install/cveforge.desktop", DESKTOP_PATH)
    shutil.copy(context.ASSETS_DIR / "favicon.png", ICON_PATH)
    OUT.print("[success]🪖 🔥 Successfully installed CVE Forge for the current user, files created 3, use debug mode to see where they are located 👊 🪖 🔥 ⚔️[/success]")
    logging.debug("Successfully written file to: %s", EXEC_PATH)
    logging.debug("Successfully written file to: %s", DESKTOP_PATH)
    logging.debug("Successfully written file to: %s", ICON_PATH)


@tcve_command(name="uninstall")
def uninstall(context: Context):
    logging.info("Uninstalling CVE Forge for the user session")

    EXEC_PATH = pathlib.Path("~/.local/bin/cveforge")
    DESKTOP_PATH = pathlib.Path("~/.local/share/applications/cveforge.desktop")
    ICON_PATH = pathlib.Path("~/.local/share/icons/hicolor/256x256/apps/cveforge.png")
    EXEC_PATH.unlink(True)
    DESKTOP_PATH.unlink(True)
    ICON_PATH.unlink(True)

    OUT.print("[success]👋🏃💨 Successfully uninstalled CVE Forge for the current user, files deleted 3, use debug mode to see where they were located[/success]")
    logging.debug("Successfully removed file in: %s", EXEC_PATH)
    logging.debug("Successfully removed file in: %s", DESKTOP_PATH)
    logging.debug("Successfully removed file in: %s", ICON_PATH)

@tcve_command(name="info")
def info(context: Context):
    commands, aliases = context.get_commands()
    body: dict[str, dict[str, TCVECommand]] = {}
    for alias in aliases.values():
        body[alias.get("command").name] = body.get(alias.get("command").name, {})
        body[alias.get("command").name][alias.get("name")] = alias
    for command in commands.values():
        body[command.get("command").name] = body.get(command.get("command").name, {})
        body[command.get("command").name][command.get("name")] = command
    formatted_body = ""
    for command in body:
        formatted_body += "|-> [green]" + command + "[/green]: " + (body[command][command].get("command").__doc__ or "").rstrip() +"\n"
        if len(body[command]) > 1:
            formatted_body += "|---> aliases: "
        for alias in body[command]:
            if alias == command:
                continue
            formatted_body += "[#222222]" + alias + "[/#222222], "
        if len(body[command]) > 1:
            formatted_body = formatted_body.removesuffix(", ")
        formatted_body += "\n\n"
    OUT.print(
        formatted_body,
    )