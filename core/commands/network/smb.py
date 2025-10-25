import getpass
from typing import Any

from core.commands.run import tcve_command
from core.context import Context
from core.io import OUT
from core.network.forge.smb import client
from utils.args import ForgeParser


class command_parser(ForgeParser):
    def setUp(self, *args: Any, **kwargs: Any) -> None:
        self.add_argument(
            "--address", "-a", help="The address to connect", required=True
        )
        self.add_argument(
            "--port",
            "-p",
            type=int,
            help="The port representing the service (if any)",
            required=False,
        )
        self.add_argument(
            "--username",
            "-u",
            help="The username to login",
            required=False,
            default=getpass.getuser(),
        )
        self.add_argument(
            "--password", "-P", help="The password to login", required=False
        )
        subparsers = self.add_subparsers(
            dest="protocol", description="the protocol to connect"
        )
        smb = subparsers.add_parser(
            "smb", description="Connect using the Server Message Block (SMB) protocol"
        )
        smb.add_argument("--share", "-s", required=False)
        smb.add_argument("--path", help="Shared path", required=False)
        netbios = subparsers.add_parser(  # type: ignore
            "netbios",
            description="Connect using the Network Basic Input Output System (NetBIOS) protocol",
        )

@tcve_command(name="protocol", parser=command_parser)
def command(context: Context, protocol: str, address: str, port: int, *args: Any, **kwargs: Any):
    if protocol == "smb":
        OUT.print("Let's do a samba! 🥳")
        try:
            with client.SMB(
                address, port or client.SMB.DEFAULT_PORT
            ) as smb:
                print(smb)

        except Exception:
            OUT.print_exception(max_frames=1)
    else:
        OUT.print(f"Connecting to: {address}:{port}")
