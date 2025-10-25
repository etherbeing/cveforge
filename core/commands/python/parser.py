from typing import Any
from utils.args import ForgeParser


class PipCommandParser(ForgeParser):
    def setUp(
        self, *args: Any, **kwargs: Any
    ):
        self.add_argument(
            "--timeout",
            "-t",
            default=10,
            type=int,
            help="Timeout to expire connection if no response (in seconds)",
        )
        self.add_argument(
            "--retries",
            "-r",
            default=5,
            help="Retries this amount in case the connection fails or epxires (-1 to retry forever)",
        )
        self.add_argument(
            "--prefer-offline",
            default=True,
            help="Whether to fetch package from local repository if available first",
        )
        self.add_argument("--ignore-cache", "-f", action="store_true", default=False)

        subparsers = self.add_subparsers(dest="command", help="Available commands")

        install = subparsers.add_parser(
            "install",
            help="Automatically handle environment and caches, if there is no index then create one. Use Symbolic Links for avoid\
replicating the data",
        )
        install.add_argument(
            "package",
        )
        install.add_argument(
            "--no-wheel",
            "-s",
            default=False,
            action="store_true",
            help="Install and build from source, don't use the wheel binaries [default: False]",
        )

        subparsers.add_parser(
            "index",
            help="""
Determine the current project package manager and system installed ones by a preset of package manages (e.g.\
pip, poetry, pipenv, etc...) and index all of their existing packages into our Forge package manager.\
Allows for avoid reinstalling packages across the packages managers and allows for later cleanup
""",
        )

        search = subparsers.add_parser(
            "search",
            help="""
Search for a package either locally or remotelly
""",
        )
        search.add_argument(
            "package",
        )
        uninstall = subparsers.add_parser(
            "uninstall",
            help="""
Uninstall a package from the current environment or upon given flag from the entire system (even from other package\
managers )
""",
        )
        uninstall.add_argument(
            "package",
        )
        import_subparser = subparsers.add_parser(
            "import",
            help="""
Import from other packages system under only one package system, this intends to be compatible with pip so it unifies
under the pip repository.
""",
        )
        import_subparser.add_argument(
            "package",
            nargs="*",
            help="""If no package given import all package into CVE Forge pip cache directory""",
        )
