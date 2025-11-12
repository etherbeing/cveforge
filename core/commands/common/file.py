import os
from pathlib import Path
from typing import Any, Optional

from core.commands.run import tcve_command
from core.commands.common.utils.filesystem.pol import pol_reader
from core.context import Context
from core.io import OUT
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
        return pol_reader(context=context, file=file)
    else:
        with open(file, mode="rb") as rfile:
            return rfile.read()


class command_cd_parser(ForgeParser):
    """Parse arguments for the CD command"""

    def setUp(self, *args: Any, **kwargs: Any) -> None:
        self.add_argument("path", nargs="?", type=lambda val: Path(val) if val else None)

@tcve_command(name="cd", parser=command_cd_parser)
def command_cd(context: Context, path: Path|None=None):
    """Change directory or current working directory into a new one"""
    os.chdir(path if path else Path.home())

class LSParser(ForgeParser):
    def setUp(self) -> None:
        self.add_argument("path", nargs="?", default=os.getcwd(), type=Path)

@tcve_command(name="ls", parser=LSParser, post_process=OUT.print)
def command_ls(context: Context, path: Path, *args: Any, **kwargs: Any): # TODO pretty print the output with colors for file, folders, links and so on
    return f"""
{", ".join([file_or_folder.name for file_or_folder in sorted(path.glob(r"*"))])}
"""