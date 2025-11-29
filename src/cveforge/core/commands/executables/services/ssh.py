from typing import Optional
import paramiko
import typer
from cveforge.core.commands.run import tcve_command
from cveforge.core.context import Context
from gettext import gettext as _


@tcve_command()
def ssh(
    uri: str = typer.Argument(default="localhost"),
    hostname: Optional[str] = typer.Option(default="localhost"),
    port: int = typer.Option(22, "--port", "-p"),
    command: Optional[str] = typer.Option(default=None),
    buffer: int = typer.Option(default=1024),
    use_password: bool = typer.Option(False, "-W"),
    identity_file: Optional[str] = typer.Option(None, "--identity", "-i"),
):
    context = Context()
    client = paramiko.SSHClient()
    parts = uri.split("@")
    if len(parts) > 1:
        username = parts.pop(0)
    else:
        username = "root"
    hostname = parts.pop(0)
    if use_password:
        password = context.console_session.prompt(_("Please enter your password: "), is_password=True)
    else:
        password = None
    # trunk-ignore(bandit/B507)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname=hostname, port=port, username=username, password=password)
    except paramiko.PasswordRequiredException:
        passphrase = context.console_session.prompt(_("Please enter the password to unlock your private key: "), is_password=True)
        client.connect(hostname=hostname, port=port, username=username, passphrase=passphrase)
    client.exec_command("id")

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
