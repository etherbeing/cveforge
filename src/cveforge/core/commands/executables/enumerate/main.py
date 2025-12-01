import paramiko
from cveforge.core.commands.run import tcve_command, tcve_option
from cveforge.core.context import Context
from django.utils.translation import gettext as _

@tcve_command()
def enumerate():
    """
    The idea of this command is to find current vulnerabilities in the given host by comparing the versions of the software and packages 
    installed in the system against the public OSINT sources that give us the vulnerabilities released
    Supports: 
        debian dpkg -l
        python
        npm
        go
        rust
        c libraries
        web

    Connects to remote host by using uri <proto>://username@host:port
    The command looks like:
    enumerate ssh://username@example.com
    enumerate http://username:password@example.com
    enumerate local://path/to/cwd/

    Optional arguments are:
        --targets os,python,npm,golang,rust,c
        --targets all
        --no-store: Do not store the data retrieved in the DB

    If you plan on doing network assessment please use nmap instead is better suited for that, you require 
    """
    pass

@tcve_option(enumerate)
def ssh():
    context: Context = Context()
    session = context.cve_sessions[-1].get_session_object()
    if session:
        if isinstance(session, paramiko.SSHClient):
            # trunk-ignore(bandit/B601)
            _i, stdout, _e = session.exec_command("dpkg -l")
            software_list = stdout.readlines()
            context.stdout.print(software_list)
        else:
            raise Exception(_("Current session object is not SSH perhaps you misspell the variant command"))
    else:
        raise Exception(_("It seems there is no session object attached to this object did you called ssh command first and established a connection?"))

@tcve_option(enumerate)
def system():
    pass

@tcve_option(enumerate)
def web():
    pass

@tcve_option(enumerate)
def sftp():
    pass
