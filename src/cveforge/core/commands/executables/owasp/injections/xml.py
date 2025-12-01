from typing import Any, Literal
from cveforge.core.sessions import CVESession

class XMLSession(CVESession):
    """
    Session class for handling XML Injection sessions.
    """
    def __init__(self, prefix: bytes, suffix: bytes, protocol: str | Literal['ssh'] | Literal['sftp'] | Literal['local'], session_object: Any = None, username: str | None = None, password: str | None = None, hostname: str | None = None, port: int | None = None, path: str | None = None) -> None:
        super().__init__(protocol, session_object, username, password, hostname, port, path)
        self._prefix = prefix
        self._suffix = suffix
