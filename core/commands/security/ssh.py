from core.commands.run import tcve_command
from core.context import Context
from gettext import gettext as _
# import paramiko

from core.io import OUT
from utils.args import ForgeParser

class SSHParser(ForgeParser):
    def setUp(self) -> None:
        self.add_argument("uri", nargs="?")
        self.add_argument("--hostname", "-H", required=False, default="localhost")
        self.add_argument("--username", "-u", required=False, default="root")
        self.add_argument("--password", "-p", required=False)
        self.add_argument("--port", "-P", required=False, type=int, default=22)
        self.add_argument("--command", "-c", required=False)
        self.add_argument("--buffer", "-b", required=True, default=1024, type=int)

@tcve_command(name="ssh", parser=SSHParser)
def command_ssh(context: Context, uri: str|None, hostname: str|None, port: int, username: str|None, password: str|None, command: str|None, buffer: int):
    import paramiko
    client = paramiko.SSHClient()
    if not uri:
        if not hostname or not username:
            raise AttributeError(_("Missing required params either use an URI or set hostname, username and password"))
    else:
        parts = uri.split("@")
        credentials = parts.pop(0).split(":")
        address = parts.pop(0).split(":")
        username = credentials.pop(0) or username
        password = credentials.pop(0) or password
        hostname = address.pop(0) or hostname
        port = int(address.pop(0) or port)
        if not hostname:
            raise AttributeError(_("Missing hostname"))
        if not port:
            raise AttributeError(_("Missing port"))
        if not username:
            raise AttributeError(_("Missing username"))
        
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hostname, port=port, username=username, password=password)
    ssh_transport = client.get_transport()
    if not ssh_transport:
        raise ValueError(_("We couldn't create a transport for the current ssh connection please try again later"))
    ssh_session = ssh_transport.open_session()
    if ssh_session.active and command:
        ssh_session.exec_command(command=command)
        OUT.print(ssh_session.recv(buffer))
    return 