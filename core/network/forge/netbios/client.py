from core.network.forge.base import Network


class NetBIOSCodes:
    SESSION_ESTABLISHED = 0x82


class NetBIOS(Network):
    def packet(self, message_type: int, payload: bytes):
        header: bytearray = bytearray(4)
        header[0] = message_type
        header[1:3] = len(payload).to_bytes(3)
        return header + payload

    def handshake(self):
        super().handshake()
        # NetBIOS Session packet
        header: bytearray = bytearray(4)
        header[0] = 0x81
        header[1] = 0x00

        called_name: bytes = str(self._address).encode()
        calling_name: bytes = self._socket.getsockname()[0].encode()
        payload = called_name + calling_name
        header[2:4] = len(payload).to_bytes(3)
        self.send(header + payload)
        response = self.recv()
        return response[0] == NetBIOSCodes.SESSION_ESTABLISHED
