from functools import lru_cache
from typing import Any

import requests

from core.commands.run import tcve_command
from core.context import Context
from core.io import OUT
from utils.args import ForgeParser
from utils.network import get_ifaces


class public_ip_parser(ForgeParser):
    def __init__(self, *args: list[Any], **kwargs: dict[str, Any]):
        super().__init__(*args, **kwargs)  # type: ignore

    def setUp(self, *args: Any, **kwargs: Any) -> None:
        self.add_argument("--interface", "-i", choices=get_ifaces().keys())

@tcve_command(name="ip", parser=public_ip_parser, post_process=OUT.print)
def public_ip(context: Context, interface: str):
    """Obtain this computer ip"""
    if interface:
        return get_ifaces().get(interface, None)
    else:

        @lru_cache
        def _network_ip():
            return requests.get("https://ifconfig.me", timeout=10).text

        return _network_ip()
