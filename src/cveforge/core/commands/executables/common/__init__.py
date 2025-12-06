"""
Common commands that are frequently used
"""

import logging
import os
import pathlib
import platform
import shutil
import stat
import subprocess
import sys
from functools import lru_cache
from typing import Literal

import typer
from rich.markdown import Markdown

from cveforge.core.commands.command_types import TCVECommand
from cveforge.core.commands.run import tcve_command
from cveforge.core.context import Context

logging.debug("Initializing common commands...")


@tcve_command(
    name="exit",
)
def cli_exit():
    """Exit the CLI"""
    sys.exit(Context().RT_OK)


@lru_cache
def _get_help(context: Context):
    help = None  # pylint: disable=redefined-builtin
    with open(context.ASSETS_DIR / "help.md", "r", encoding="utf8") as file:
        help = file.read()
    return Markdown(help)


@tcve_command(name="help")
def cli_help():
    """Help command"""
    context: Context = Context()
    context.stdout.print(_get_help(context))


@tcve_command()
def restart():
    """
    Reload the current process by spawning a detached child process
    and terminating the current one.
    """
    sys.exit(Context().EC_RELOAD)

@tcve_command(name="env")
def command_env():
    """
    Return environment data for the current context that this Forge is running on
    """
    context: Context = Context()
    context.stdout.print(f"""
{platform.platform()} {platform.machine()} {" ".join(platform.architecture())}
{platform.python_implementation()}: {" ".join(platform.python_build())} {platform.python_compiler()}

{"\n".join([f"{item[0]}={item[1]}" for item in os.environ.items()])}
""")


@tcve_command()
def log(
    message: str = typer.Argument(),
    level: Literal["DEBUG", "INFO", "ERROR", "WARNING"] = typer.Option(default="DEBUG"),
):
    """
    Log the given message to the console as it would be logged to the file, this is useful for testing logging capabilities
    """
    context: Context = Context()
    int_level: int = logging.getLevelNamesMapping().get(level, logging.DEBUG)
    logging.basicConfig(filename=None, force=True)
    logging.log(level=int_level, msg=" ".join(message))
    context.stdout.print(
        "[green]Printed given data into the configured output file[/green]"
    )
    context.configure_logging(context.log_level)


@tcve_command()
def install():
    context = Context()
    try:
        if os.getuid() != 0:
            raise PermissionError("You must run this as sudo")
        logging.info(
            "Installing CVE Forge in the user session, system-wide installation is NOT supported yet"
        )

        EXEC_PATH = pathlib.Path("~/.local/bin/cveforge").expanduser()
        DESKTOP_PATH = pathlib.Path(
            "~/.local/share/applications/cveforge.desktop"
        ).expanduser()
        ICON_PATH = pathlib.Path(
            "~/.local/share/icons/hicolor/256x256/apps/cveforge.png"
        ).expanduser()
        NGINX_PATH = pathlib.Path("/etc/nginx/sites-enabled/cveforge")

        shutil.copy(context.ASSETS_DIR / ".install/cveforge.sh", EXEC_PATH)
        exec_content = None
        desktop_content = None

        with open(EXEC_PATH, "r", encoding="utf-8") as file:
            exec_content = file.read()
        with open(EXEC_PATH, "w", encoding="utf-8") as file:
            file.write(
                exec_content.format(
                    ABSOLUTE_PATH=context.BASE_DIR.absolute().parent.parent
                )
            )

        os.chmod(EXEC_PATH, EXEC_PATH.stat().st_mode | stat.S_IEXEC)

        shutil.copy(context.ASSETS_DIR / ".install/cveforge.desktop", DESKTOP_PATH)

        with open(DESKTOP_PATH, "r", encoding="utf-8") as file:
            desktop_content = file.read()
        with open(DESKTOP_PATH, "w", encoding="utf-8") as file:
            file.write(
                desktop_content.format(
                    EXEC_PATH=EXEC_PATH.absolute(), ICON_PATH=ICON_PATH.absolute()
                )
            )

        shutil.copy(
            context.ASSETS_DIR / ".install/nginx-cveforge.conf", NGINX_PATH
        )  # Requires root
        with open(NGINX_PATH, "r", encoding="utf-8") as file:
            nginx_content = file.read()
        with open(NGINX_PATH, "w", encoding="utf-8") as file:
            file.write(
                nginx_content.format(
                    TCP_MAIN_PORT=context.web_address.split(":", 1)[1],
                    STATIC_ROOT=context.STATIC_DIR,
                    MEDIA_ROOT=context.MEDIA_DIR,
                )
            )

        shutil.copy(context.ASSETS_DIR / "favicon.png", ICON_PATH)
        context.stdout.print(
            "[success]🪖 🔥 Successfully installed CVE Forge for the current user, files created 4, use debug mode to see where they are located 👊🪖 🔥⚔️[/success]"
        )
        logging.info("Successfully written file to: %s", EXEC_PATH)
        logging.info("Successfully written file to: %s", DESKTOP_PATH)
        logging.info("Successfully written file to: %s", ICON_PATH)
        logging.info("Successfully written file to: %s", NGINX_PATH)
        subprocess.run(["uv", "run", "src/cveforge/manage.py", "collectstatic"])
        subprocess.run(["nginx", "-s", "reload"])
    except PermissionError as ex:
        raise ex
    except Exception as ex:
        logging.error("Failed to install due to %s", str(ex))
        uninstall.run(context)


@tcve_command()
def uninstall():
    context = Context()
    logging.info("Uninstalling CVE Forge for the user session")
    if os.getuid() != 0:
        raise PermissionError("You must run this as sudo")

    EXEC_PATH = pathlib.Path("~/.local/bin/cveforge").expanduser()
    DESKTOP_PATH = pathlib.Path(
        "~/.local/share/applications/cveforge.desktop"
    ).expanduser()
    ICON_PATH = pathlib.Path(
        "~/.local/share/icons/hicolor/256x256/apps/cveforge.png"
    ).expanduser()
    NGINX_PATH = pathlib.Path("/etc/nginx/sites-enabled/cveforge")

    EXEC_PATH.unlink(True)
    DESKTOP_PATH.unlink(True)
    ICON_PATH.unlink(True)
    NGINX_PATH.unlink(True)

    context.stdout.print(
        "[success]👋🏃💨 Successfully uninstalled CVE Forge for the current user, files deleted 3, use debug mode to see where they were located[/success]"
    )
    logging.info("Successfully removed file in: %s", EXEC_PATH)
    logging.info("Successfully removed file in: %s", DESKTOP_PATH)
    logging.info("Successfully removed file in: %s", ICON_PATH)


@tcve_command()
def info():
    context: Context = Context()
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
        formatted_body += (
            "|-> [green]"
            + command
            + "[/green]: "
            + (body[command][command].get("command").__doc__ or "").rstrip()
            + "\n"
        )
        if len(body[command]) > 1:
            formatted_body += "|---> aliases: "
        for alias in body[command]:
            if alias == command:
                continue
            formatted_body += "[#222222]" + alias + "[/#222222], "
        if len(body[command]) > 1:
            formatted_body = formatted_body.removesuffix(", ")
        formatted_body += "\n\n"
    context.stdout.print(
        formatted_body,
    )
