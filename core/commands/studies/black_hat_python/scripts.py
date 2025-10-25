import socket

from prompt_toolkit import PromptSession

from core.commands.run import tcve_command
from core.commands.studies.black_hat_python.parsers import CommandParser
from core.context import Context
from core.exceptions.ipc import ForgeException
from core.io import OUT


class TCPClient:
    def __init__(self) -> None:
        self._socket: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP
        )

    def connect(self, target_ip: str, target_port: int):
        self._socket.connect((target_ip, target_port))

    def http_send(self, path: str = "/", content: str | None = None):
        self._socket.send(
            f"""
GET {path} HTTP/1.1\r\nHost: google.com\r\n
""".encode()
        )
        return self._socket.recv(4096)


class UDPClient:
    def __init__(self) -> None:
        self._socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        )

    def send(self, data: bytes, target_ip: str, target_port: int):
        self._socket.sendto(data, (target_ip, target_port))
        self._socket.settimeout(5)
        return self._socket.recvfrom(4096)


class TCPServer:
    def __init__(self, timeout: int = 5):
        self._socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP
        )
        self._socket.settimeout(timeout)

    def listen(self, host: str, port: int):
        self._socket.bind((host, port))
        self._socket.listen()
        sock, _ = self._socket.accept()
        sock.send(b"reply")
        return sock.recv(4096)


@tcve_command("book_bhp", post_process=OUT.print, parser=CommandParser)
def scripts_command(
    context: Context,
    command: str,
    type: str | None = None,
    server: bool = False,
    host: str = "localhost",
    port: int = 8000,
):
    session = PromptSession[str]()
    if command == "tcp" and type == "http" and not server:
        OUT.print("HTTP/TCP Client")
        client = TCPClient()
        client.connect(host, port)
        response = client.http_send()
        return response
    elif command == "tcp" and server:
        return TCPServer().listen(host, port)
    elif command == "udp":
        OUT.print("UDP Client")
        client = UDPClient()
        return client.send(
            session.prompt("Please set the data you wanna send: ").encode(), host, port
        )
    else:
        OUT.print("Command not implemented")
        raise ForgeException(code=10)
