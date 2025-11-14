import threading

from daphne.cli import CommandLineInterface
from cveforge.core.commands.run import tcve_command
from cveforge.core.context import Context
from cveforge.utils.args import ForgeParser


class ServerParser(ForgeParser):
    def setUp(self) -> None:
        self.add_argument("--join", "-J", default=False, action="store_true")


@tcve_command("cve_forge_api", parser=ServerParser, auto_start=True, hidden=True, run_once=True)
def main(context: Context, join: bool):
    THREAD_API_NAME = "CVE Forge Web"
    try:
        server_thread = next(filter(lambda t: t.name == THREAD_API_NAME,threading.enumerate()))
    except StopIteration:
        cli = CommandLineInterface()
        host, port = context.web_address.split(":")
        log_file = context.log_file.parent / ".web_access"
        log_file.touch(mode=0o755)
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
                    "--access-log",
                    log_file.__str__(),
                    "cveforge.web.cve_forge.asgi:application",
                ]
            ],
            daemon=True,
            name=THREAD_API_NAME
        )
        server_thread.start()
        if join:
            server_thread.join()
        return cli
