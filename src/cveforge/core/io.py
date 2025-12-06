from types import TracebackType
from typing import Optional
from rich.progress import Progress, SpinnerColumn, TaskID, TextColumn, ProgressColumn


class ForgeConsole:
    """Wrapper around the rich console for easier of usage"""

    def __init__(self, no_progress: bool=False) -> None:
        self._progress: Progress
        self._default_task_id: TaskID
        self._no_progress = no_progress

    def print(self, msg: str, *args: str, task_id: Optional[TaskID] = None):
        self._progress.update(task_id or self._default_task_id, description=msg)

    def __enter__(
        self,
    ):
        args: list[str | ProgressColumn] = [
            SpinnerColumn(),
            TextColumn("{task.description}"),
        ]
        self._progress = Progress(
            *args,
            transient=False,
            expand=True,
        ).__enter__()
        self._default_task_id = self._progress.add_task(description="")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        self._progress.__exit__(exc_type=exc_type, exc_val=exc_val, exc_tb=exc_tb)
