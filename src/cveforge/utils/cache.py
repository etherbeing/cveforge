from typing import Any, Callable, Optional


class tcve_cache: # TODO Nothing is implemented yet
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._callable: Optional[Callable[..., Any]] = None
        
    def __call__(self, callable: Callable[..., Any], *args: Any, **kwds: Any) -> Any:
        if not self._callable:
            self._callable = callable
        return callable