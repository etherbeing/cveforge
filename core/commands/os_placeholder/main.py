import sys
# trunk-ignore(bandit/B404)
from subprocess import call

from core.commands.run import tcve_command
from core.context import Context

from .parser import Parser


@tcve_command(
    "bash",
    parser=Parser,
    aliases=["echo", "curl", "clear", "pwd", "ss", "watch", "ping"],
)
def main(context: Context, params: list[str]):
    cc = context.command_context.get("current_command") or {}
    current_command = cc.get("name", "")
    call(
        [current_command, *params],
        stdout=context.console_session.output.fileno(),
        stderr=sys.stderr,
        stdin=context.console_session.input.fileno(),
        shell=False,
    )
