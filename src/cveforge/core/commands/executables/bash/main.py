import sys

# trunk-ignore(bandit/B404)
from subprocess import call
from typing import Annotated, Optional

import typer

from cveforge.core.commands.run import tcve_command
from cveforge.core.context import Context


@tcve_command(
    aliases=["echo", "curl", "clear", "pwd", "ss", "watch", "ping", "ls", "cd", "cat", "tail", "head", "grep"],
)
def bash(params: Annotated[Optional[list[str]], typer.Argument()] = None):
    """
    List of commands available directly available from batch, this is just an alias to bash command and you can still use them all by using @ before the name
    """
    context = Context()
    params = params or []
    cc = context.command_context.get("current_command") or {}
    current_command = cc.get("name", "")
    call(
        [current_command, *params],
        stdout=context.console_session.output.fileno(),
        stderr=sys.stderr,
        stdin=context.console_session.input.fileno(),
        shell=False,
    )
