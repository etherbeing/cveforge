"""
Handle dynamic module loading for better performance
"""

import importlib
import pathlib
import sys


def refresh_modules(in_scope: str|pathlib.Path, exclude: list[str|pathlib.Path]|None=None):
    in_scope = str(in_scope)
    exclude = [str(path) for path in exclude] if exclude else [pathlib.Path(in_scope)/".venv"]
    eligible_modules = dict(
        list(
            filter(
                lambda module_item: (
                    getattr(module_item[1], "__file__", None) and not module_item[0].startswith("_") and (module_item[1].__file__ or "").startswith(in_scope) and 
                    all([not (module_item[1].__file__ or "").startswith(str(path)) for path in exclude])
                ), 
                sys.modules.items()
            )
        )
    )
    for module_item in eligible_modules.items():
        importlib.reload(module_item[1])
        # setattr(new_module, "__last_refreshed__", datetime.now())
    return eligible_modules
