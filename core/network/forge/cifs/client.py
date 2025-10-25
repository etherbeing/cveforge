import ipaddress
import logging
import socket
from socket import SocketKind  # pylint: disable=no-name-in-module
from types import TracebackType


class CIFS:
    sock_type: SocketKind = socket.SOCK_RAW

    def __init__(self, address: str, port: int) -> None:
        assert 0 < port < 65535, "Port must be valid"
        self._port = port
        self._address = ipaddress.ip_address(address)
        if self._address.version == 4:
            self._socket = socket.socket(socket.AF_INET, self.sock_type)
        else:
            self._socket = socket.socket(socket.AF_INET6, self.sock_type)

    def connect(
        self,
    ):
        """
        Establish a protocol connection in the TCP layer with the server
        """
        logging.debug(f"CIFS connecting to params: {self._address}:{self._port}")
        self._socket.connect((str(self._address), self._port))

    def handshake(self):
        """
        Exchange the first the first protocol messages to establish a broader gamma of options
        for protocol usage
        """
        logging.debug("Running server handshake")
        self._socket.settimeout(3)
        self._socket.send(b"NEGOTIATE_PROTOCOL_REQUEST")
        data = self._socket.recv(1024)
        logging.debug(data)

    def __enter__(
        self,
    ):
        """
        Use this class prefferable in a context manager something like:
        ```py
        with CIFS('127.0.0.1') as cifs:
            cifs.smb.lsShares()
        ```
        """
        self.connect()
        self.handshake()
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
