"""
Handle sudo command
"""

import logging
from typing import cast

from core.context import Context
from core.exceptions.ipc import ForgeException
from utils.sudo import is_admin

try:
    from multiprocessing.connection import Connection
except ImportError:
    from multiprocessing.connection import PipeConnection as Connection # type: ignore


def sudo_handler(
        pipe: Connection, # type: ignore
        context: Context
    ):
    """
    Call this method with multiprocessing.run or similar to create a process that have
    elevated privileges after that you can use in a normal process with no elevated
    privileges a Pipe to pass commands to this process and use them in a privileged way
    """
    while is_admin():  # if privileges are lost then go out of the loop
        logging.debug("On sudo process, waiting for commands...")
        command: list[str] = cast(list[str], pipe.recv()) # type: ignore
        if not command:
            logging.debug("No command provided, skipping...")
            continue
        else:
            cve_command = context.get_commands()[1].get(command[0], None)
            if not cve_command:
                raise ForgeException("Invalid command provided")
            else:
                command_method = cve_command.get("command")
                if not command_method:
                    raise DeprecationWarning(f"{cve_command.get("name")} method wasn't loaded as you're using a deprecated feature")
                else:
                    command_method.run(context, extra_args=command[1:])
