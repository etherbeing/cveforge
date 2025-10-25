import logging
import socket
from types import TracebackType
from typing import Any

from core.io import OUT
from core.network.forge.base import Network
from core.network.forge.cveforge.server import ForgeNetworkServer


class ForgeNetworkClient(Network):
    """Client side to communicate with the CVE Forge custom protocol"""

    sock_type = socket.SOCK_STREAM
    proxy_response: int
    is_persistent: bool = False

    @property
    def proxy_enabled(
        self,
    ):
        """Returns whether or not the proxy is enabled or not"""
        return self.proxy_response == ForgeNetworkServer.RTCodes.OK

    @property
    def proxy_too_many_connections(
        self,
    ) -> bool:
        """Parse and return a pythonic usable state for the proxy response"""
        return self.proxy_response == ForgeNetworkServer.RTCodes.MAX_CONNECTIONS

    def enable_proxy(
        self,
    ):
        self._socket.send(ForgeNetworkServer.RTCodes.ENABLE_PROXY.to_bytes(1))
        self.proxy_response = int.from_bytes(self._socket.recv(1))
        return self.proxy_response

    def persist(self, value: bool = True):
        self.is_persistent = value

    def packet(
        self, payload: bytes, target_address: str, port: int, *args: Any, **kwargs: Any
    ) -> bytes:
        OUT.print(f"{target_address}{port}{payload.decode()}")
        return payload

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        if not self.is_persistent:
            logging.debug("Closing non persistent socket at the end of context manager")
            return self.close()

    def close(
        self,
        exc_type: type[BaseException] | None = None,
        exc_val: BaseException | None = None,
        exc_tb: TracebackType | None = None,
    ):
        """Atomic close operation for avoid client side persistency"""
        logging.debug(
            "Closing socket and other resources opened due to call on close function"
        )
        return super().__exit__(exc_type=exc_type, exc_val=exc_val, exc_tb=exc_tb)
