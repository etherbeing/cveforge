from argparse import Namespace
from pathlib import Path

from core.commands.python import CacheStorage
from core.commands.python.install import pip_install
from core.commands.python.parser import PipCommandParser
from core.commands.python.pip_import import pip_import
from core.commands.python.search import pip_search
from core.commands.run import tcve_command
from core.context import Context

PIP_LOCK_FILE = Path("requirements.txt")  # following pip standards


@tcve_command("pip", parser=PipCommandParser)
def command(namespace: Namespace, context: Context):
    """
    pip alternative to work in high latency network and unreliable networks.
    Feature: Resume from where it failed last

    """
    assert (
        context.data_dir is not None
    ), "Error on PIP command as data_dir is currently None"
    storage = CacheStorage(context.data_dir / ".pipenvs", "pip_packages.json")
    # 1. Search in cache
    # 2. Continue from where it was left
    # 3. Store metadata
    if namespace.command == "search":
        return pip_search(namespace, storage, is_verbose=True)
    elif namespace.command == "install":
        return pip_install(namespace, storage, context)
    elif namespace.command == "import":
        return pip_import(namespace, storage)
    return ""
