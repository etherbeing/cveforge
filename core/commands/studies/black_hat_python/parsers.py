from typing import Any
from utils.args import ForgeParser


class CommandParser(ForgeParser):
    def setUp(self, *args: Any, **kwargs: Any) -> None:
        command = self.add_subparsers(
            dest="command",
        )
        self.add_argument("--host", default="localhost")
        self.add_argument("--port", default=8000, type=int)
        tcp_parser = command.add_parser(
            "tcp",
        )
        tcp_parser.add_argument(
            "--server",
            action="store_true",
        )
        tcp_subparsers = tcp_parser.add_subparsers(dest="type")
        tcp_subparsers.add_parser(
            "http",
        )

        command.add_parser("udp")
