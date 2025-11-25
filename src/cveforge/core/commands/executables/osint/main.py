# https://osintframework.com/arf.json

import logging
import requests
from cveforge.core.commands.run import tcve_command
from cveforge.core.context import Context


@tcve_command(categories=["information", "osint", "intelligence"])
def osint():
    """
    OSINT [Open Source Intelligence] command allows you to search for intelligence online, users, info and so on....
    """
    context: Context = Context()
    arf = requests.get('https://osintframework.com/arf.json', timeout=context.http_timeout)
    arf.raise_for_status()
    arf = arf.json()
    logging.warning("NOT IMPLEMENTED YET, communication with the osing framework working...")