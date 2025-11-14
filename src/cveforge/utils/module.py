"""
Handle dynamic module loading for better performance
"""

import importlib
import importlib.util
import logging
import pathlib
import sys


def refresh_modules(in_scope: str|pathlib.Path, exclude: list[str|pathlib.Path]|None=None):
    in_scope = str(in_scope)
    exclude = [str(path) for path in exclude] if exclude else []
    exclude.insert(0, pathlib.Path(in_scope)/".venv")
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
        try:
            importlib.reload(module_item[1])
        except Exception as exc:
            logging.error("Failed to reload the module %s due to %s", module_item[0], str(exc))
    return eligible_modules


def load_module_from_path(path: pathlib.Path, module_name: str|None = None):
    if module_name is None:
        module_name = path.stem  

    spec = importlib.util.spec_from_file_location(module_name, str(path))
    module = None
    if spec:
        module = importlib.util.module_from_spec(spec)
        if spec.loader:
            spec.loader.exec_module(module)
            sys.modules[module_name] = module
    return module