from typing import Optional

import typer
from cveforge.core.commands.run import tcve_command
from cveforge.core.context import Context
from gettext import gettext as _

@tcve_command()
def ssh(
    context: Context,
    uri: Optional[str] = typer.Argument(),
    hostname: Optional[str] = typer.Option(default="localhost"),
    port: Optional[int] = typer.Option(default=22),
    username: Optional[str] = typer.Option(default="root"),
    password: Optional[str] = typer.Option(),
    command: Optional[str] = typer.Option(),
    buffer: int = typer.Option(default=1024),
):
    import paramiko

    client = paramiko.SSHClient()
    if not uri:
        if not hostname or not username:
            raise AttributeError(
                _(
                    "Missing required params either use an URI or set hostname, username and password"
                )
            )
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

    # trunk-ignore(bandit/B507)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hostname, port=port, username=username, password=password)
    ssh_transport = client.get_transport()
    if not ssh_transport:
        raise ValueError(
            _(
                "We couldn't create a transport for the current ssh connection please try again later"
            )
        )
    ssh_session = ssh_transport.open_session()
    if ssh_session.active and command:
        # trunk-ignore(bandit/B601)
        ssh_session.exec_command(command=command)
        context.stdout.print(ssh_session.recv(buffer))
    return
