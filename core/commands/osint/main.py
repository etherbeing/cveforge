# https://osintframework.com/arf.json

import logging
import requests
from core.commands.osint.parser import OSINTParser
from core.commands.run import tcve_command
from core.context import Context


@tcve_command("osint", parser=OSINTParser, categories=["information", "osint", "intelligence"])
def osint(context: Context):
    """
    OSINT [Open Source Intelligence] command allows you to search for intelligence online, users, info and so on....
    """
    arf = requests.get('https://osintframework.com/arf.json', timeout=context.http_timeout)
    arf.raise_for_status()
    arf = arf.json()
    logging.warning("NOT IMPLEMENTED YET, communication with the osing framework working...")