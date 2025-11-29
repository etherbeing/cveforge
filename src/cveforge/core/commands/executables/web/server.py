import logging
import threading

from daphne.server import Server
from daphne.utils import import_by_path
from daphne.endpoints import build_endpoint_description_strings
from asgiref.compatibility import guarantee_single_callable
import typer
from cveforge.core.commands.run import tcve_command
from cveforge.core.context import Context


def start_server():
    context = Context()
    host, port = context.web_address.split(":", 1)
    application = import_by_path("cveforge.web.cve_forge.asgi:application")
    application = guarantee_single_callable(application)

    # Build endpoint description strings from (optional) cli arguments
    endpoints: list[str] = build_endpoint_description_strings(
        host=host,
        port=int(port),
    )
    logging.info("Starting server at {}".format(", ".join(endpoints)))
    server = Server(
        application=application,
        endpoints=endpoints,
        action_logger=None,
        verbosity=0,
        proxy_forwarded_address_header="X-Forwarded-For",
        proxy_forwarded_port_header="X-Forwarded-Port",
        proxy_forwarded_proto_header=("X-Forwarded-Proto"),
        server_name=context.SOFTWARE_NAME,
    )
    server.run()


@tcve_command(name="api", auto_start=True, hidden=True)
def main(join: bool = typer.Option(default=False)):
    THREAD_API_NAME = "CVE Forge Web"
    try:
        server_thread = next(
            filter(lambda t: t.name == THREAD_API_NAME, threading.enumerate())
        )
    except StopIteration:
        server_thread = threading.Thread(
            target=start_server,
            daemon=True,
            name=THREAD_API_NAME,
        )
        server_thread.start()
        if join:
            server_thread.join()
