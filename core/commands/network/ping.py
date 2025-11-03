import ipaddress
import socket
import struct
import time
from typing import Any

from core.commands.run import tcve_command
from core.context import Context
from core.io import ForgeConsole
from utils.args import ForgeParser

ICMP_ECHO_REQUEST = 8


def checksum(data: bytes):
    """Calculate the checksum for the data."""
    if len(data) % 2:
        data += b"\x00"
    checksum = sum((data[i] << 8) + data[i + 1] for i in range(0, len(data), 2))
    checksum = (checksum >> 16) + (checksum & 0xFFFF)
    checksum += checksum >> 16
    return ~checksum & 0xFFFF


def create_packet(identifier: int, sequence_number: int):
    """Create a new ICMP Echo Request packet."""
    header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, 0, identifier, sequence_number)
    data = struct.pack("d", time.time())
    packet_checksum = checksum(header + data)
    header = struct.pack(
        "!BBHHH",
        ICMP_ECHO_REQUEST,
        0,
        socket.htons(packet_checksum),
        identifier,
        sequence_number,
    )
    return header + data


class ping_parser(ForgeParser):
    def setUp(self, *args: Any, **kwargs: Any) -> None:
        self.add_argument(
            "address",
        )
        self.add_argument("--timeout", "-t", default=1)
        self.add_argument(
            "--tcp",
            "-T",
            action="store_true",
            help="Use TCP packets for the payload requests, check for the ACK after SYN requests",
        )
        self.add_argument("--retries", "-r", default=5)

@tcve_command(name="ping", parser=ping_parser)
def ping(context: Context, address: str, tcp: bool=False, timeout: int=1, retries: int=5):
    """Ping a host and return the latency."""
    from scapy.all import (  # all of these is imported here to avoid requesting for admin UAC at startup
        sr,
    )
    from scapy.layers.inet import ICMP, IP, TCP
    from scapy.layers.inet6 import IPv6

    with ForgeConsole() as console:
        # retries: int = namespace.retries
        target_address = ipaddress.ip_address(socket.gethostbyname(address))
        print(target_address)
        if target_address.version == 4:
            packet = IP(dst=str(target_address))
        else:
            packet = IPv6(dst=str(target_address))
        packet.setfieldval("ttl", 64)
        if tcp:
            recv_packet = sr(packet / TCP(dport=80, flags="S"))
        else:
            recv_packet = sr(packet / ICMP())
        if not recv_packet:
            console.print("No packet received")
        else:
            recv_packet[0].show()
        # while True:
        #     retries -= 1
        #     if retries == 0:
        #         break
        #     if recv_packet:
        #         console.print(f"Received packet from {recv_packet.src}")
        #         continue
