"""
Handle the server for the Forge protocol
"""

import ipaddress
import logging
import socket
import threading
from types import TracebackType

from core.io import OUT
from core.network.forge.base import Network
from core.network.forge.cveforge.server_core.rce import handle_rce
from core.network.forge.socket import ForgeSocket


class ForgeNetworkServer(Network):
    """Server implementation for the CVE Forge custom network protocol"""

    sock_type = socket.SOCK_STREAM
    _server_thread: threading.Thread
    _max_connections: int = 10  # max number of threads used for responding clients
    _client_threads: dict[str, threading.Thread] = {}

    class RTCodes:
        """Return codes and protocols codes for the CVE Forge protocol"""

        OK = 0x00
        ENABLE_PROXY = 0x01
        MAX_CONNECTIONS = 0x02
        EXIT = 0x03
        # WARNING This must be handled pretty cautiously as it is intended for when the
        # user is run as sudo
        REMOTE_CODE_EXECUTION = 0x04
        # Meta data
        BYTE_SIZE = 1
        PROXY_TIMEOUT = 60
        PROXY_TARGET_SIZE = 32  # For storing even IPv6 address
        PROXY_PORT_SIZE = 4

    def __enter__(self):
        try:
            self._socket.bind((str(self._address), self._port))
        except OSError as error:
            logging.error(
                "Cannot successfully bind the socket with the given address %s:%s because: %s",
                self._address,
                self._port,
                error,
            )
            OUT.print_exception()
            exit(self._context.RT_ADDRESS_IN_USE)
        self._server_thread = threading.Thread(
            target=self._listen,
            name="Forge Network Server: Context Mode"
        )
        logging.debug("Starting server thread for listening to incoming connections")
        self._server_thread.start()  # Start to listen for incoming connections
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        try:
            self._server_thread.join()
        except (RuntimeError, KeyboardInterrupt):
            pass
        return super().__exit__(exc_type, exc_val, exc_tb)

    def _client_thread(
        self, client_socket: ForgeSocket, client_address: tuple[str, int]
    ):
        action = int.from_bytes(
            client_socket.recv(self.RTCodes.BYTE_SIZE)
        )  # First the client send an action package just 1 byte
        if action == self.RTCodes.ENABLE_PROXY:
            client_socket.settimeout(self.RTCodes.PROXY_TIMEOUT)
            try:
                client_socket.send(int.to_bytes(self.RTCodes.OK))
                while True:
                    # The live connection between the client and the proxy server requires
                    # a header of 36 bytes containing
                    # first part 32 bytes, an ipv4 or ipv6 address as the target
                    # second part 4 bytes, a tcp port for the target
                    # client_data = os.read(client_socket.fileno(), self.RTCodes.PROXY_TARGET_SIZE)
                    client_data = client_socket.recv(
                        self.RTCodes.PROXY_TARGET_SIZE, socket.MSG_WAITALL
                    )
                    if not client_data:
                        logging.debug(
                            "Connection from %s:%s dropped",
                            client_address[0],
                            client_address[1],
                        )
                        client_socket.close()
                        break

                    ip_address = ipaddress.ip_address(client_data)
                    tcp_port = int.from_bytes(
                        client_socket.recv(
                            self.RTCodes.PROXY_PORT_SIZE, socket.MSG_WAITALL
                        )
                    )
                    target_sock = socket.socket(
                        socket.AF_INET if ip_address.version == 4 else socket.AF_INET6,
                        self.sock_type,
                    )
                    if self.sock_type == socket.SOCK_STREAM:
                        target_sock.connect((str(ip_address), tcp_port))
                    target_sock.send(client_socket.recv(self.buffer))
                    logging.debug(
                        """Proxying from %s:%s through this server(%s:%s) to %s:%s""",
                        client_address[0],
                        client_address[1],
                        self._address,
                        self._port,
                        ip_address,
                        tcp_port,
                    )
            except TimeoutError:
                logging.debug("Socket timeout")
                client_socket.close()
        elif (
            action == self.RTCodes.REMOTE_CODE_EXECUTION
            and self._context.enable_sudo_rce
        ):
            handle_rce(
                from_socket=client_socket, context=self._context
            )  # WARNING ZONE as this is intended for handling commands when in sudo and escalate privileges locally
        else:
            logging.info(
                "Unknown param from connection %s:%s",
                client_address[0],
                client_address[1],
            )
        del self._client_threads[threading.current_thread().name]

    def _listen(
        self,
    ):
        logging.debug("On server listen thread, setting the socket in listening mode")
        self._socket.listen()
        while True:
            logging.debug("Waiting for incoming connections...")
            client_sock, client_addr = self._socket.accept()
            logging.debug("New connection from %s:%s", client_addr[0], client_addr[1])
            if len(self._client_threads) >= self._max_connections:
                client_sock.send(self.RTCodes.MAX_CONNECTIONS.to_bytes(1))
                client_sock.close()
                logging.error(
                    "Connection rejected for client %s:%s",
                    client_addr[0],
                    client_addr[1],
                )
                continue
            ct = threading.Thread(
                target=self._client_thread,
                kwargs={"client_socket": client_sock, "client_address": client_addr},
                name=f"{client_addr[0]}:{client_addr[1]}",
            )
            self._client_threads[ct.name] = ct
            ct.start()
