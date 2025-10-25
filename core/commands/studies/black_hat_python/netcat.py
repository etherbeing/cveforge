import ipaddress
import logging
import socket
import subprocess
import threading
from typing import Any, Literal

from prompt_toolkit import PromptSession

from core.commands.run import tcve_command
from core.commands.studies.black_hat_python.netcat_parser import NetcatParser
from core.context import Context
from core.exceptions.ipc import ForgeException
from core.io import OUT


class Netcat:
    def __init__(
        self,
        address: ipaddress.IPv4Address | ipaddress.IPv6Address,
        buffer: int,
        timeout: int,
        protocol: Literal["udp", "tcp"] = "tcp",
    ):
        if address.version == 4:
            af = socket.AF_INET
        elif address.version == 6:
            af = socket.AF_INET6
        else:
            raise ForgeException("Invalid attributes passed")
        if protocol == "tcp":
            sk = socket.SOCK_STREAM
        elif protocol == "udp":
            sk = socket.SOCK_DGRAM
        else:
            raise ForgeException("Invalid attributes passed")
        self._address: ipaddress.IPv4Address | ipaddress.IPv6Address = address
        self._protocol = protocol
        self._socket: socket.socket = socket.socket(af, sk)
        self._socket.settimeout(timeout)
        self._timeout = timeout
        self._buffer = buffer

    def start_server(self, port: int, foreground: bool = False):
        self._socket.bind((str(self._address), port))

        def _thread_server():
            logging.debug("Running inside the thread")
            self._socket.listen()

            def _client_thread(client_sock: socket.socket, address: socket.AddressInfo):
                logging.debug("New connection from %s", addr)
                while True:
                    command = client_sock.recv(self._buffer).decode()
                    logging.debug("Received command %s", command)
                    if command.startswith(Context.SYSTEM_COMMAND_TOKEN):
                        command = command.removeprefix(
                            Context.SYSTEM_COMMAND_TOKEN
                        ).strip()
                        output = subprocess.check_output(
                            command, stderr=client_sock.fileno(), shell=True
                        )
                        client_sock.send(output)
                    else:
                        client_sock.send(command.encode())  # echo behavior
                        if command == "quit":
                            break
                client_sock.close()

            while True:
                sock, addr = self._socket.accept()
                try:
                    threading.Thread(
                        target=_client_thread,
                        name="Netcat Server: Listener",
                        kwargs={"client_sock": sock, "address": addr},
                    ).start()
                except TimeoutError:
                    sock.close()
                    self._socket.close()
                    break

        logging.info("Server running on port %s", self._address)
        if foreground:
            _thread_server()
        else:
            threading.Thread(
                target=_thread_server,
                name="Netcat Server: Runner"
            ).start()  # this makes the server non blocking

    def start_client(self, port: int):
        try:
            self._socket.connect((str(self._address), port))
            session = PromptSession[str]()

            while True:
                prompt = session.prompt("> ")
                try:
                    if prompt == "clear":
                        OUT.clear()
                        continue
                    self._socket.send(prompt.encode())

                    if False:
                        chunk: bytes = b""
                        raw_response: bytes = b""
                        while len(chunk := self._socket.recv(self._buffer)):
                            raw_response += chunk
                            if not len(chunk):
                                break

                        response = raw_response.decode()
                    else:
                        response = self._socket.recv(self._buffer).decode()

                    if response == "quit":
                        self._socket.close()
                        break
                    OUT.print("< " + response)
                except BrokenPipeError:
                    self._socket.close()
                    break
            # Use prompt and create a nice tool to communicate with the backend
        except KeyboardInterrupt:
            try:
                self._socket.close()
            except:
                pass


@tcve_command("netcat", parser=NetcatParser)
def command(
    context: Context,
    port: int,
    listen: str,
    buffer: int,
    timeout: int,
    target: str | None = None,
    foreground: bool = False,
    **kwargs: Any,
):
    netcat = Netcat(
        address=ipaddress.ip_address(listen), buffer=buffer, timeout=timeout
    )
    if target:
        netcat.start_client(port=port)
    else:
        netcat.start_server(port=port, foreground=foreground)
