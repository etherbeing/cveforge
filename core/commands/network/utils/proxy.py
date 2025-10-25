"""
Proxy command command management
"""

import logging
from typing import Any

from core.commands.run import tcve_command
from core.context import Context
from core.network.forge.cveforge.client import ForgeNetworkClient, ForgeNetworkServer
from utils.args import ForgeParser


class command_parser(ForgeParser):
    """
    Parser for the proxy command
    """

    PROXY_DEFAULT_PORT = 6660
    PROXY_SERVER_START_O = "start"
    PROXY_SERVER_CONNECT_O = "connect"

    def setUp(self, *args: Any, **kwargs: Any) -> None:
        subparsers = self.add_subparsers(dest="option")
        start = subparsers.add_parser(
            self.PROXY_SERVER_START_O,
        )
        start.add_argument("--listen", "-l", type=str, default="0.0.0.0")
        start.add_argument("--port", "-p", type=int, default=6660)
        connect = subparsers.add_parser(self.PROXY_SERVER_CONNECT_O)
        connect.add_argument("--address", "-a", required=True, type=str)
        connect.add_argument("--port", "-p", default=self.PROXY_DEFAULT_PORT, type=int)


def proxy_server_start(listen: str, port: int, context: Context):
    """
    Start the proxy server, this help us to do various tasks as
    proxying our communication through a third party host using our own
    custom protocol or also running remote code execution from our host.
    The idea of the proxy is for using locally alongside tools like WSL
    in windows.
    """
    logging.info("Starting Forge Proxy <%s:%s>", listen, port)
    with ForgeNetworkServer(address=listen, port=port, context=context):
        logging.info(
            "Server successfully started, now listening for incoming connections"
        )


def proxy_server_connect(address: str, port: int, context: Context):
    """
    Proxy server connect is used for connecting to a proxy server under the Forge protocol
    which is encrypted and allows RCE and other stuff
    """
    logging.info("Starting Forge Proxy client through <%s:%s>", address, port)
    with ForgeNetworkClient(
        address=address, port=port, context=context
    ) as proxy_client:
        logging.info(
            "Proxy client is up and running, enabling it now for global usage..."
        )
        proxy_client.enable_proxy()
        if proxy_client.proxy_enabled:
            logging.info("Proxy successfully enabled")
            context.set_proxy_client(proxy_client)
            proxy_client.persist()
        elif proxy_client.proxy_too_many_connections:
            logging.error(
                "[red]Proxy couldn't be enabled successfully due to the server "
                "unsatisfactory response, right now there is too many active connections[/red]"
            )
        else:
            logging.error(
                "[red]Proxy couldn't be enabled successfully due to the "
                "server unsatisfactory response, please check the server and try again[/red]"
            )

@tcve_command(name="proxy", parser=command_parser)
def command(context: Context, option: str, address: str, port: int, listen: str|None=None, connect: bool=False):
    """
    Command to start a proxy server or connect to a proxy
    """
    assert listen or connect
    if option == command_parser.PROXY_SERVER_START_O:
        assert listen
        proxy_server_start(
            listen=listen, port=port, context=context
        )
    elif option == command_parser.PROXY_SERVER_CONNECT_O:
        proxy_server_connect(
            address=address, port=port, context=context
        )
