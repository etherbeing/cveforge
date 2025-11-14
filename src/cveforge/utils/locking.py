from pathlib import Path

from cveforge.core.exceptions.ipc import ForgeException


class FileRecordLocking:
    """
    A lightweight file-locking mechanism using lock files.
    This class does not implement true file record locking but prevents
    simultaneous file access by processes through `.lock` files.
    """

    FRL_EXT = ".lock"
    _locked_file: Path

    def __init__(self, path: Path) -> None:
        self._path = path

    def __enter__(
        self,
    ):
        self._locked_file = Path(str(self._path) + self.FRL_EXT)
        try:
            self._locked_file.touch(exist_ok=False)
        except FileExistsError as ex:
            raise ForgeException(
                f"""\
{self._path.name} is locked by another process, perhaps in another machine or session, if this is wrong please delete {
self._locked_file.absolute()
}"""
            ) from ex

    def __exit__(self, *args: str, **kwargs: str):
        self._locked_file.unlink(False)
