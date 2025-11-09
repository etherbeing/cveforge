import threading

from daphne.cli import CommandLineInterface

from core.commands.run import tcve_command
from core.context import Context
from utils.args import ForgeParser


class ServerParser(ForgeParser):
    def setUp(self) -> None:
        self.add_argument("--join", "-J", default=False, action="store_true")


@tcve_command("cve_forge_api", parser=ServerParser, auto_start=True)
def main(context: Context, join: bool):
    cli = CommandLineInterface()
    host, port = context.web_address.split(":")
    server_thread = threading.Thread(
        target=cli.run,
        args=[
            [
                "-b",
                host,
                "-p",
                port,
                "-v",
                str(context.LOG_LEVEL // 10),
                "-s",
                context.SOFTWARE_NAME,
                "web.cve_forge.asgi:application",
            ]
        ],
        daemon=True,
    )
    server_thread.start()
    if join:
        server_thread.join()
