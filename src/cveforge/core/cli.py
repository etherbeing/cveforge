from typing import TYPE_CHECKING, Any, Iterable, Optional
import typer
if TYPE_CHECKING:
    from cveforge import Context


class CVEForgeExecutable:
    def __init__(self) -> None:
        self._context: Optional[Context] = None
        self._typer: Optional[typer.Typer] = None
        self._cli: dict[str, Any] = {}

    def set_context(self, context: 'Context'):
        self._context = context
    
    def set_root_typer_app(self, app: typer.Typer):
        self._typer = app
        self._typer.command(name="cveforge")(self)

    def prepare(self, args: Iterable[str]):
        """
        Using typer and the given args parse the args for this instance and return the kwargs that are
        to be used for the execution stage
        """
        if self._typer:
            self._typer(args=list(args), standalone_mode=False)

    def execute(self):
        pass

    def execute_async(self):
        pass

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass

    @property
    def typer(self):
        return self._typer