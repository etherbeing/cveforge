import logging
import socket
from dataclasses import dataclass

from core.network.forge.netbios.client import NetBIOS
from core.network.forge.smb.security.base import DIALECT_NAMES, Dialect


@dataclass
class SMBPacket:
    header: bytes = b"\xffSMB"
    command: bytes = b"\x72" * 1  # Defaults to negotiate command
    error: bytes = b"\x00" * 4
    flags: bytes = b"\x00" * 1
    flags2: bytes = b"\x00" * 2
    pid_high: bytes = b"\x00" * 2
    security_features: bytes = b"\x00" * 16
    reserved: bytes = b"\x00" * 2
    tid: bytes = b"\x00" * 2
    pid_low: bytes = b"\x00" * 2
    uid: bytes = b"\x00" * 2
    mid: bytes = b"\x00" * 2

    def to_bytes(
        self,
    ):
        return b"".join(self.__dict__.values())


class SMB(NetBIOS):
    """Server Message Block message implementation"""

    DEFAULT_PORT = 139
    sock_type = socket.SOCK_STREAM
    _PROTOCOL_HEADER = b"\xffSMB"

    def __init__(
        self,
        address: str,
        port: int = DEFAULT_PORT,
        direct: bool = False,
        dialect: DIALECT_NAMES = "ntlm",
    ) -> None:
        super().__init__(address, port)
        self._direct = direct
        self._dialect = Dialect.name_to_dialect(dialect)

    def packet(self, message_type: int, payload: bytes):
        header = bytearray(32)
        header[0:4] = b"\xffSMB"
        header[4] = message_type  # SMB Command
        header[5:9] = b"\x00\x00\x00\x00"  # Error status
        header[9] = 0b0000_0000  # First flag
        header[10:11] = [0b0000_0000, 0b0000_0000]  # Flags 2
        header[11:12] = b"\x00\x00"  # PID High
        header[12:20] = b"\x00\00\00\00\00\00\00\00"  # Signature
        header[20:22] = b"\x00\x00"  # Reserved
        header[22:24] = b"\x00\x00"  # Tree ID (TID)
        header[24:26] = b"\x00\x00"  # PID Low
        header[26:28] = b"\x00\x00"  # User ID (UID)
        header[28:30] = b"\x00\x00"  # MultiplexID (MUID)

        request = bytearray(3)
        request[0] = 0x00
        request[1:2] = len(payload).to_bytes(2)
        request += payload
        return super().packet(message_type, (header + request))

    def negotiate(
        self,
    ):
        """Custom part of the SMB logic"""
        packet = self.packet(0x72, self._dialect.to_header())  # type: ignore
        # if self._dialect:
        #     packet = SMBPacket(
        #         security_features=self._dialect.to_header()
        #     ).to_bytes()
        # else:
        #     packet = SMBPacket().to_bytes()

        logging.debug(f"Negotiation request: {packet}")
        # assert len(header) == 32, "Sorry but the length of the header must be 32 and it is: %s"%len(header)
        self.send(packet)
        response = self.recv()
        logging.debug(f"Negotiation response: {response.decode()}")

    def handshake(self):
        if not self._direct:
            super().handshake()
        # Negotiate
        self.negotiate()
        # Authentication
        return True
