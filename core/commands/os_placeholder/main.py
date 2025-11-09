from subprocess import call
import sys

from core.commands.run import tcve_command
from core.context import Context
from .parser import Parser


@tcve_command("aircrack-ng", parser=Parser, aliases=["echo"])
def main(context: Context, params: list[str]):
    cc = context.command_context.get("current_command") or {} 
    current_command = cc.get("name", "")
    call(
        [
        current_command,
        *params
        ],
        stdout=sys.stdout,
        stderr=sys.stderr,
        stdin=sys.stdin,
        shell=False
    )