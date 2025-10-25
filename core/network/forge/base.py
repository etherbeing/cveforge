import ipaddress
import logging
import socket
from socket import SocketKind  # pylint: disable=no-name-in-module
from types import TracebackType
from typing import Any

from core.context import Context
from core.network.forge.socket import ForgeSocket


class Network:
    """Handle common network connection and socket manipulation"""

    sock_type: SocketKind = socket.SOCK_RAW
    buffer: int = 1024
    sock_timeout: int = 10

    def __init__(
        self,
        address: str,
        port: int,
        context: Context,  # Instance for the context object to avoid reinstantiating it
    ) -> None:
        assert 0 < port < 65535, "Port must be valid"
        self._port = port
        self._address = ipaddress.ip_address(address)
        if self._address.is_unspecified:
            self._address = ipaddress.ip_address(
                socket.gethostbyname(str(self._address))
            )
        if self._address.version == 4:
            self._socket = socket.socket(socket.AF_INET, self.sock_type)
        else:
            self._socket = ForgeSocket(socket.AF_INET6, self.sock_type, context=context)
        self._context = context

    def connect(
        self,
    ):
        """
        Establish a protocol connection in the TCP layer with the server
        """
        logging.debug("Connecting to params: %s:%i", self._address, self._port)
        self._socket.connect((str(self._address), self._port))
        self._socket.settimeout(self.sock_timeout)

    def handshake(self) -> bool:
        """
        Exchange the first protocol messages to establish a broader gamma of options
        for protocol usage
        """
        logging.debug("Running server handshake")
        return False

    def authenticate(
        self,
    ) -> bool:
        return False

    def packet(self, payload: bytes, *args: Any, **kwargs: Any) -> bytes:
        """Implement protocol packeting"""
        return payload

    def unpack(self, payload: bytes) -> bytes:
        return payload

    def send(self, data: bytes):
        return self._socket.send(data)

    def recv(
        self,
    ):
        return self.unpack(
            self._socket.recv(
                self.buffer,
            )
        )

    def encrypt(self, payload: bytes):
        pass

    def decrypt(self, payload: bytes):
        pass

    def __enter__(
        self,
    ):
        """
        Use this class preferable in a context manager something like:
        ```py
        with Network('127.0.0.1') as network:
            network.do_something()
        ```
        """
        self.connect()
        self.handshake()
        self.authenticate()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        self._socket.close()

    def __del__(
        self,
    ):
        self._socket.close()

    def __str__(
        self,
    ):
        return f"{self._address}:{self._port}"
