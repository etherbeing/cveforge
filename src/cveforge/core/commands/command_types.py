from typing import Any, Callable, NotRequired, Optional, TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from cveforge.core.commands.run import tcve_command

TCVECommand = TypedDict(
    "TCVECommand",
    {
        "name": str,
        "command": 'tcve_command',
        "post-process": NotRequired[Optional[Callable[..., Any]]],
    },
)
