from typing import Literal

import typer
from cveforge.core.commands.run import tcve_command


@tcve_command()
def scaffold(option: Literal["plugin", "command"] = typer.Argument()):
    pass