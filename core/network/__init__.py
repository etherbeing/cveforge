from socket import socket, AF_INET, SOCK_RAW

class Network:
    """
    Handle network communication including socket management, high latency networks, NAT hold pushing, and other network issues
    using python how to elevate my current script to admin requesting sudo permission or in windows UAP ?
    """
    def __init__(self) -> None:
        self._socket = socket(AF_INET, SOCK_RAW)
    
    def connect(self, address: str, port: str):
        pass
