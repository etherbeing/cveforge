from pathlib import Path
from typing import Any, Optional
from core.commands.run import tcve_command
from .utils.filesystem.pol import pol_reader
from core.context import Context
from utils.args import ForgeParser


class command_open_parser(ForgeParser):
    def setUp(self, *args: Any, **kwargs: Any) -> None:
        self.add_argument("file", type=Path)


def get_type(file: Path) -> Optional[str]:
    parts: list[str] = str(file)[::-1].split(".", 1)
    if not (len(parts) > 1):
        return None  # as there is no extension in the file TODO implement a way to obtain the file type by extension
    ext: str = parts[0][::-1]  # reverse it again as we alread reversed it before
    # name = parts[1][::-1]
    return ext.lower()

@tcve_command(name="open", parser=command_open_parser)
def command_open(context: Context, file: Path):
    """
    Handle file open in the CVE Forge context
    """
    if not file.exists():
        raise FileNotFoundError(
            f"{file} does not exist, please check for any typo"
        )
    if get_type(file) == "pol":
        context.stdout.print(pol_reader(context=context, file=file))
    else:
        with open(file, mode="rb") as rfile:
            context.stdout.print(rfile.read())
