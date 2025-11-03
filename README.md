# CVE Forge: The framework for exploits

The goal of this project is to make CVE development fast and easy by providing a framework that allows quick exploits development.

## Quickstart

**NOTE: This is a TODO meaning is YET to be implemented**
```sh
poetry init # helps you to work in a virtualenv
poetry add cve_forge # add the cve_forge dependency
poetry run cve_forge scaffold payload --verbose-name WannaCry # add to the forge DB the path to the current project
poetry run cve_forge scaffold exploit --verbose-name "RSA Cracking" --cve-name cve_2025_0002 # add to the forge DB the path to the current project
poetry run cve_forge scaffold command --verbose-name "sftp" # add to the forge DB the path to the current project
poetry run cve_forge # now whenever we modify the payload, the exploit or the command project the cve_forge self-refresh
```

## Developing a Malware or Payload

Please note that even though this software allows to create and use malware is intended for authorized pentesting only, with the idea in mind of helping malware
develop is not causing unauthorize damage but quickly letting clients know how much can impact a vulnerability into their system.

PR including malware WON'T be merged instead malware development is exclusive for the team responsible of developing this software as countermeasure for safe
usage is to be taken (NOTE: this can change in the future when we run this software in an isolated environment)

## Developing a command

As you may have noticed this project is a shell like software, you can use command like ping, ip etc... with the only caveat that all commands are to be made using python, even though we support payload development with Rust, we won't be integrating with Rust for exploits or command as this doesn't offer any benefit
except for speed AFAIC.

Once you do the quickstart step for developing a command you'd have two pieces of structures a ForgeParser and a decorated function.

### The ForgeParser
The parser is the part of the code that parse the user input and turn it into your function requirements or what is the same the part that turns commands flags
into function keywords arguments.

```py
from cve_forge import ForgeParser

class YourParser(ForgeParser):
    def setUp(self): # Here you may setup your command metadata as its name and arguments
        self.add_argument("--my-flag")
```

### The command entrypoint
```py
from cve_forge import tcve_command
from cve_forge import Context
from .parser import YourParser
import logging


@tcve_command("your_command_name", parser=YourParser)
def your_parser(context: Context, my_flag: str):
    logging.info("Running your command with flag '%s'", my_flag)
```

You may never add defaults on your function definition and rather use the parser defined default when adding your argument.

### Usage:
```sh
your_command_name --my-flag "CVE Forge is amazing!!!" # output: info: Running your command with flag 'CVE Forge is amazing!!!'
```

## Developing an Exploit or PoC for CVEs

Developing an exploit is just like creating a command but rather than using the @tcve_command we use the @tcve_exploit like follows:

```py
from cve_forge import tcve_exploit

@tcve_exploit("cve_2025_0001", categories=["cve", "privilege escalation"])
def main(context: Context, **kwargs):
    pass
```
Note the categories is also a possible command for the @tcve_command decorator, is useful for allowing the user to search with different queries for your command
