"""
Entrypoint and executable for CVE Forge
author: etherbeing
license: Apache
"""

import logging
import multiprocessing
import threading
import sys
from collections.abc import Callable

from core.context import Context
from core.io import OUT
from entrypoint import main
from utils.development import FileSystemEvent, Watcher


def live_reload_trap(live_reload_watcher: Watcher, child:multiprocessing.Process)->Callable[..., None]:
    def _trap(event: FileSystemEvent):
        return live_reload_watcher.do_reload(event, child)
    return _trap

if __name__ == "__main__":
    with Context() as context:
        threading.main_thread().name = "CVEF Executor"
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

        live_reload = None
        if context.live_reload:
            live_reload = Watcher(context=context)
            live_reload.observer.name = "CVEF File Observer"
            watcher = live_reload.start(context.BASE_DIR)


        while True:
            # Running the main process in a child process to be able to handle live reload and other IPC events
            worker_thread = threading.Thread(
                target=main,
                name=context.SOFTWARE_NAME,
                daemon=False,
                kwargs={"context": context},
            )
            worker_thread.start()
            if live_reload:
                live_reload.live_reload = live_reload_trap(live_reload_watcher=live_reload, child=worker_thread) # type: ignore
                worker_thread.join()
                del sys.modules["entrypoint"]
                from entrypoint import main
                if context.exit_status == context.EC_EXIT:
                    break
            else:
                worker_thread.join()
                if context.exit_status == context.EC_RELOAD:
                    del sys.modules["entrypoint"]
                    from entrypoint import main
                    continue
                break

        if live_reload:
            live_reload.stop()

        logging.debug(
            "Child exit code, processed successfully exiting now..."
        )
        OUT.print(
            "[green] 🚀💻 See you later, I hope you had happy hacking! 😄[/green]"
        )
        exit(context.RT_OK)
