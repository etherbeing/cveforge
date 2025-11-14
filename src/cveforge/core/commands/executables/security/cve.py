from typing import Any
from core.commands.exploits import ExploitParser
from core.commands.run import tcve_command
from core.context import Context

@tcve_command(name="exploit", parser=ExploitParser)
def exploit(context: Context, option: str, command: str, *args: Any, **kwargs: Any):
    return ExploitParser.run_exploit(command, context, option, **kwargs)