"""
Handle dynamic module loading for better performance
"""

import importlib
import logging
import sys
from functools import lru_cache


@lru_cache
def load_module(module: str, name: str):
    """
    Dynamically load and cache
    """
    try:
        package = sys.modules.get(module)
        if not package:
            package = importlib.import_module(module)
        return getattr(package, name, None)
    except (ImportError, AttributeError, FileNotFoundError) as ex:
        logging.debug("You were searching for %s in %s but %s", name, module, ex)
        return None
