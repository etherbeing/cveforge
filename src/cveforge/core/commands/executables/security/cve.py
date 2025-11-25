from typing import Annotated, Any, Optional

import typer
from cveforge.core.commands.run import tcve_command, tcve_exploit, tcve_option
from cveforge.core.context import Context
from cveforge.utils.osint.vulmon import consult

@tcve_command()
def exploit():
    pass

def exploit_ready(*args: Any, **kwargs: Any):
    tcve_exploit.set_exploit_command(exploit)

exploit.register("ready", exploit_ready)

@tcve_option(exploit)
def run(command_name: str = typer.Argument(), args: Annotated[Optional[list[str]], typer.Argument()] = None):
    """
    Run an exploit using the exploit expected params
    """
    pass
    # return tcve_exploit.run(command_name, args)

@tcve_option(exploit)
def scan(target_uri: str=typer.Argument()):
    pass

@tcve_option(exploit)
def patch(vulnerability: str=typer.Argument()):
    pass

@tcve_option(exploit)
def search(query: str=typer.Argument()):
    context= Context()
    cves: dict[str, Any] = consult(query)
    # for name, value in cves.items():
    #     pass
    context.stdout.print("Searching %s"%query)
    context.stdout.print("Found %s"%cves)

