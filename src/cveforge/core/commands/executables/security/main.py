from typing import Annotated, Any, Optional

import typer
from cveforge.core.commands.run import tcve_command, tcve_exploit, tcve_option
from cveforge.core.context import Context
from cveforge.utils.osint.vulmon import consult as vulmon_consult
from cveforge.utils.osint.cwe import consult as cwe_consult


@tcve_command()
def exploit():
    pass


def exploit_ready(*args: Any, **kwargs: Any):
    tcve_exploit.set_exploit_command(exploit)


exploit.register("ready", exploit_ready)


@tcve_option(exploit)
def run(
    command_name: str = typer.Argument(),
    args: Annotated[Optional[list[str]], typer.Argument()] = None,
):
    """
    Run an exploit using the exploit expected params
    """
    pass


@tcve_option(exploit)
def scan(target_uri: str = typer.Argument()):
    pass


@tcve_option(exploit)
def patch(vulnerability: str = typer.Argument()):
    pass


@tcve_option(exploit, is_command=True)
def search(query: str = typer.Argument()):
    context = Context()
    cves: dict[str, Any] = vulmon_consult(query)
    cwes: dict[str, Any] = cwe_consult(query)
    # for name, value in cves.items():
    #     pass
    context.stdout.print("Searching %s" % query)
    context.stdout.print("Found CWEs %s" % cwes)
    context.stdout.print("Found CVEs %s" % cves)
