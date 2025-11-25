from functools import lru_cache
from typing import Optional

import requests
import typer

from cveforge.core.commands.run import tcve_command
from cveforge.core.context import Context
from cveforge.utils.network import get_ifaces


@tcve_command()
def ip(interface: Optional[str] = typer.Option(default=None)):
    """Obtain this computer ip"""
    context: Context = Context()
    if interface:
        context.stdout.print(get_ifaces().get(interface, None))
    else:

        @lru_cache
        def _network_ip():
            return requests.get("https://ifconfig.me", timeout=10).text

        context.stdout.print(_network_ip())
