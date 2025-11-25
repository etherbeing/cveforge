from typing import Literal

import typer
from cveforge.core.commands.run import tcve_command
from cveforge.core.context import Context


@tcve_command()
def scaffold(option: Literal["plugin", "command"] = typer.Argument()):
    _ = Context()
    pass