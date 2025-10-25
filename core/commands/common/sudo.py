import logging
import multiprocessing
from argparse import Namespace
from typing import Any

from core.commands.run import tcve_command
from core.context import Context
from core.exceptions.ipc import ForgeException
from utils.args import ForgeParser
from utils.sudo import elevate_privileges, is_admin # type: ignore


class command_parser(ForgeParser):
    """
    Parser for the command sudo
    """

    def setUp(self, *args: Any, **kwargs: Any) -> None:
        self.add_argument(
            "command", help="Run the given command as superuser", nargs="+"
        )


@tcve_command("sudo", parser=command_parser)
def command(namespace: Namespace, context: Context):
    """
    Run the given command as superuser
    """
    logging.debug("User requested to run command %s as super user", namespace.command)
    if is_admin():
        logging.debug("User is already an admin, running the command")
        cve_command = context.get_commands().get(namespace.command)
        if not cve_command:
            raise ForgeException("Invalid command provided")
        cve_command.get("command").run(context)
    elif context.sudo_pipe: # type: ignore
        logging.debug("User is not an admin, sending the command to the sudo process")
        context.sudo_pipe.send(namespace.command) # type: ignore
    elif not context.sudo_pipe: # type: ignore
        logging.debug(
            "User is not an admin and there is no sudo process running, spawning the sudo process, requesting now for sudo access"
        )
        pipes = multiprocessing.Pipe()
        context.sudo_pipe = pipes[
            0
        ]  # store in this process global context the pipe to communicate with the sudo process

        elevate_privileges(pipe=pipes[1], context=context)
