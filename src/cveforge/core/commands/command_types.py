from typing import Any, Callable, NotRequired, Optional, TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from cveforge.core.commands.run import tcve_base

TCVECommand = TypedDict(
    "TCVECommand",
    {
        "name": str,
        "command": 'tcve_base',
        "post-process": NotRequired[Optional[Callable[..., Any]]],
    },
)
