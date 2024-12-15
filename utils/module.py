"""
Handle dynamic module loading for better performance 
"""
from functools import lru_cache
import importlib
import importlib.util
import sys


# def load_exploit(exploit_name: str):
#     pass

@lru_cache
def load_module(module: str, name: str):
    """
        Dynamically load and cache 
    """
    try:
        package = sys.modules.get(module)
        if not package:
            package = importlib.import_module(module)
        return getattr(package, name)
    except (ImportError, AttributeError):
        return None
