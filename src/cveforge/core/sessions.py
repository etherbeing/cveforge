from typing import Any, Literal, Optional


from cveforge.core.commands.command_types import TCVECommand


class CVESession:
    """
    If we should proxify(send requests through an specific place) any request so when we have an opened session commands go to the target session instead this is is the middleware for that
    """

    @property
    def protocol(self):
        return self._protocol

    def __init__(
        self,
        protocol: Literal["ssh", "sftp", "local"] | str,
        session_object: Any = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        hostname: Optional[str] = None,
        port: Optional[int] = None,
        path: Optional[str] = None,
    ) -> None:
        self._protocol = protocol
        self._session_object = session_object
        self._username = username
        self._password = password
        self._hostname = hostname
        self._port = port
        self._path = path

    def __str__(self) -> str:
        formatted_text = ""
        formatted_text += self._protocol + "://"
        if self._username:
            formatted_text += self._username
            if self._password:
                formatted_text += ":" + "*" * 8
        if self._hostname:
            if self._username:
                formatted_text += "@"
            formatted_text += self._hostname
            if self._port:
                formatted_text += ":" + str(self._port)
        if self._path:
            formatted_text += self._path
        return formatted_text

    def run(self, command: TCVECommand, *args: Any, **kwargs: Any):
        return command.get("command").run(*args, **kwargs)

    def get_session_object(self):
        return self._session_object

    def __bool__(
        self,
    ):
        return self._protocol != "local"
