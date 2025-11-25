import os
import pathlib
import subprocess
import sys
from typing import Optional
from typing_extensions import Annotated

import typer

from cveforge.core.commands.run import tcve_command
from cveforge.core.context import Context


@tcve_command()
def sudo(
    command: str = typer.Argument(),
    remainder: Annotated[Optional[list[str]], typer.Argument()] = None,
):
    remainder = remainder or []
    context: Context = Context()
    if os.getuid() != 0:  # TODO make it compatible with windows as well
        context.console_session.app.refresh_interval = 0
        python_bin = None
        try:
            return subprocess.run(
                [
                    "sudo",
                    "-E",
                    "--",
                    str(context.BASE_DIR.parent.parent / "scripts/pythonpath_run.sh"),
                    subprocess.check_output(["which", "uv"], text=True).strip(),
                    command,
                    *remainder,
                ],
                env=os.environ,
            )
        except subprocess.CalledProcessError:
            VENV_ENV = os.getenv("VIRTUAL_ENV")
            if VENV_ENV:
                virtualenv_path = pathlib.Path(VENV_ENV)
                if virtualenv_path.exists():
                    virtual_bin = virtualenv_path / "bin/python"
                    if virtual_bin.exists():
                        python_bin = virtual_bin
            if not python_bin:
                python_bin = sys.executable
            subprocess.run(
                ["sudo", python_bin, context.BASE_DIR, "command", *remainder],
            )
    else:
        commands, aliases = context.get_commands()
        available_commands = commands | aliases
        cmd = available_commands.get(command)
        if not cmd:
            raise ValueError("Not found")
        else:
            return cmd.get("command").run(context, *remainder)
