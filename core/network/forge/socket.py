"""
Socket related file
"""

from socket import socket
from typing import Any

from typing_extensions import Buffer

from core.context import Context


class ForgeSocket(socket):
    """Context aware socket, with auto-proxying capabilities"""

    def __init__(self, *args: Any, context: Context, **kwargs: str) -> None:
        super().__init__(*args, **kwargs)
        self._context = context

    def send(self, data: Buffer, flags: int = 0) -> int:
        if self._context.proxy_client:
            ta, tp = self.getpeername()
            packed_data = self._context.proxy_client.packet(
                payload=bytes(data), target_address=ta, port=tp
            )
            return self._context.proxy_client.send(data=packed_data)
        else:
            return super().send(data, flags)
