from typing import Any
from cveforge.core.commands.run import tcve_command
from cveforge.core.context import Context
from cveforge.utils.args import ForgeParser


class ScaffoldParser(ForgeParser):
    def setUp(self, *args: Any, **kwargs: Any) -> None:
        option_subparser = self.add_subparsers(title="option", help="Scaffold a plugin directory with the default files needed")
        option_subparser.add_parser("plugin", help="Scaffold a plugin directory with the default files needed")
        option_subparser.add_parser("command", help="Scaffold a command directory so it contains all the needed files to add a new command to CVE Forge")

@tcve_command(parser=ScaffoldParser, name="scaffold")
def scaffold(context: Context, option: str):
    pass