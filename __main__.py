#!/usr/bin/env python3
"""
Entrypoint and executable for CVE Forge
author: etherbeing
license: Apache
"""

import multiprocessing
from core.context import Context
# from core.io import OUT
from entrypoint import main
from utils.development import Watcher



if __name__ == "__main__":
    live_reload = Watcher()
    watcher = live_reload.start(Context.BASE_DIR)
    while True:
        child = multiprocessing.Process(target=main)
        child.start()
        live_reload.live_reload = lambda event: live_reload.do_reload(event, child)
        while (
            True
        ):  # needed to avoid respawning the processes if an accidental Keyboard interrupt reach 
            # here
            try:
                child.join() # in case the live reload exited normally for some reason
                break  # just run once but Keyboard interrupts is ignored
            except KeyboardInterrupt:
                continue
        if child.exitcode == Context.EC_RELOAD or live_reload.reload:
            live_reload.reload = False
            continue  # respawn the child process
        else:
            break
