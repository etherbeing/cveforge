"""
Remote Code Execution management file, it is responsible for sanitizing and handling the commands to execute
"""

import logging

from core.context import Context
from core.network.forge.base import Network
from core.network.forge.socket import ForgeSocket


def handle_rce(from_socket: ForgeSocket, context: Context):  # pylint: disable=W0613
    """
    Handle Remote Code Execution requests from the client
    """
    command: str = from_socket.recv(Network.buffer).decode()
    logging.debug("Client running Remote Code Execution: %s", command)
    base = command.split()
    args: list[str] = []
    if len(base) > 1:
        args: list[str] = base[1:]
    base = base[0]
    cve_command = context.get_commands().get(str(base), None)
    if not cve_command:
        logging.error("Client trying to run a non existing command %s", command)
        return None  # Return now and keep doing wtv you were doing as the client requested something impossible 😄
    else:
        from_socket.send(
            b"Implementing command yet please wait a little bit until ready, you said: %s %s"
            % (base, args)
        )
