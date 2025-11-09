"""
Entrypoint and executable for CVE Forge
author: etherbeing
license: Apache
"""

import logging
import multiprocessing
from collections.abc import Callable

from core.context import Context
from core.exceptions.ipc import ForgeException
from core.io import OUT
from entrypoint import main
from utils.development import FileSystemEvent, Watcher


def live_reload_trap(live_reload_watcher: Watcher, child:multiprocessing.Process)->Callable[..., None]:
    def _trap(event: FileSystemEvent):
        return live_reload_watcher.do_reload(event, child)
    return _trap


if __name__ == "__main__":
    with Context() as context:
        logging.basicConfig(
            level=context.LOG_LEVEL,
            format=context.LOG_FORMAT,
            datefmt=context.LOG_DATE_FTM,
        )
        if context.argv_command:
            context.configure_logging()
            logging.debug("Running command directly from the command line")
            args = []
            if len(context.argv_command) > 1:
                args = context.argv_command[1:]
            base = context.argv_command[0]
            local_commands, _  = context.get_commands()
            cve_command = local_commands.get(
                base,
            )
            if cve_command:
                logging.debug("Running command %s with args %s", cve_command, args)
                command_method = cve_command.get("command")
                if not command_method:
                    raise DeprecationWarning(f"{cve_command.get("name")} method wasn't loaded as you're using a deprecated feature")
                else:
                    command_method.run(context, extra_args=args)
                exit(context.RT_OK)
            else:
                OUT.print(
                    f"[red]Invalid command given, {context.argv_command} is not recognized as an internal command of CVE Forge[/red]"
                )
                exit(context.RT_INVALID_COMMAND)
        pipe = multiprocessing.Pipe()
        if not context.LIVE:
            live_reload = Watcher(pipe[1], context=context)
            watcher = live_reload.start(context.BASE_DIR)
        else:
            live_reload = None
            watcher = None
        while True:
            # Running the main process in a child process to be able to handle live reload and other IPC events
            child = multiprocessing.Process(
                target=main,
                name=context.SOFTWARE_NAME,
                daemon=False,
                kwargs={"pipe": pipe[1], "context": context},
            )
            child.start()
            if live_reload:
                live_reload.live_reload = live_reload_trap(live_reload_watcher=live_reload, child=child) # type: ignore
            logging.debug(
                "Child process ended with code %s, now processing the exit status",
                child.exitcode,
            )
            try:
                child.join()
                ipc_object = pipe[0].recv()  # Block here until IPC data is received
            except EOFError:
                ipc_object = None
            except KeyboardInterrupt:
                break
            close_normally_attempts = 3

            for _ in range(close_normally_attempts):
                child.terminate()
                if not child.is_alive():
                    break
            else:
                child.kill()

            if isinstance(ipc_object, ForgeException):
                if ipc_object.code == context.EC_RELOAD and live_reload:
                    logging.debug(
                        "Child exit code seems to be a request to reload, relaunching program again"
                    )
                    live_reload.reload = True
                    continue  # re-spawn the child process
                else:
                    logging.debug(
                        "Child exit code, processed successfully exiting now..."
                    )
                    OUT.print(
                        "[green] 🚀💻 See you later, I hope you had happy hacking! 😄[/green]"
                    )
                    break
            else:
                continue  # Only ForgeException is allowed to finish the program
        exit(context.RT_OK)
