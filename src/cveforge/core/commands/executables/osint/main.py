# https://osintframework.com/arf.json

import logging
from typing import Optional
import requests
import typer
from cveforge.core.commands.run import tcve_command


@tcve_command(categories=["information", "osint", "intelligence"])
def osint(http_timeout: Optional[int] = typer.Option(default=10, help="HTTP request timeout in seconds")):
    """
    OSINT [Open Source Intelligence] command allows you to search for intelligence online, users, info and so on....
    """
    arf = requests.get('https://osintframework.com/arf.json', timeout=http_timeout)
    arf.raise_for_status()
    arf = arf.json()
    logging.warning("NOT IMPLEMENTED YET, communication with the osing framework working...")