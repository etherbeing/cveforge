from functools import lru_cache
from argparse import ArgumentParser, Namespace
from typing import Any
import requests

from utils.network import get_ifaces

class public_ip_parser(ArgumentParser):
    def __init__(self, *args: list[Any], **kwargs: dict[str, Any]):
        super().__init__(*args, **kwargs) # type: ignore
        self.add_argument(
            "--interface", "-i",
            choices=get_ifaces().keys()
        )

def public_ip(namespace: Namespace):
    """Obtain this computer ip"""
    if namespace.interface:
        return get_ifaces().get(namespace.interface, None)
    else:
        @lru_cache
        def _network_ip():
            return requests.get("https://ifconfig.me", timeout=10).text
        return _network_ip()
