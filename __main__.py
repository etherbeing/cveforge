"""
Entrypoint and executable for CVE Forge
author: etherbeing
license: Apache
"""

import logging
import threading
from time import sleep
from collections.abc import Callable

from core.context import Context
from core.io import OUT
from utils.development import FileSystemEvent, Watcher
from utils.module import refresh_modules
# trunk-ignore(ruff/F401)
import entrypoint # type: ignore  # noqa: F401

def live_reload_trap(
    live_reload_watcher: Watcher, child: threading.Thread
) -> Callable[..., None]:
    def _trap(event: FileSystemEvent):
        return live_reload_watcher.do_reload(event, child)

    return _trap


if __name__ == "__main__":
    with Context() as context:
        threading.main_thread().name = "CVE Forge Executor"
        context.configure_logging()

        if context.argv_command:
            logging.debug("Running command directly from the command line")
            args = []
            if len(context.argv_command) > 1:
                args = context.argv_command[1:]
            base = context.argv_command[0]
            local_commands, aliases = context.get_commands()
            available_commands = local_commands | aliases
            cve_command = available_commands.get(
                base,
            )
            if cve_command:
                logging.debug("Running command %s with args %s", cve_command, args)
                command_method = cve_command.get("command")
                if not command_method:
                    raise DeprecationWarning(
                        f"{cve_command.get('name')} method wasn't loaded as you're using a deprecated feature"
                    )
                else:
                    context.command_context.update({"current_command": cve_command})
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
            live_reload.observer.name = "CVE Forge File Observer"
            watcher = live_reload.start(context.BASE_DIR)

        while True:
            context.get_commands.cache_clear()
            modules = refresh_modules(str(context.BASE_DIR.absolute()))
            
            # Running the main process in a child process to be able to handle live reload and other IPC events
            worker_thread = threading.Thread(
                target=modules["entrypoint"].main,
                name=context.SOFTWARE_NAME,
                daemon=False,
                kwargs={"context": context, "modules": modules},
            )
            worker_thread.start()
            if live_reload:
                live_reload.live_reload = live_reload_trap(
                    live_reload_watcher=live_reload, child=worker_thread
                )  # type: ignore
                worker_thread.join()

                if context.exit_status == context.EC_EXIT:
                    break
                else:
                    sleep(1.5)
            else:
                worker_thread.join()
                if context.exit_status == context.EC_RELOAD:
                    sleep(1.5)
                    continue
                break

        if live_reload:
            live_reload.stop()

        logging.debug("Child exit code, processed successfully exiting now...")
        OUT.print(
            "[green] 🚀💻 See you later, I hope you had happy hacking! 😄[/green]"
        )
        exit(context.RT_OK)
