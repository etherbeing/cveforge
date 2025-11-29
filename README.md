# CVE Forge: A Unified, Actionable Penetration Testing Framework

CVE Forge is a framework inspired by [metasploit](https://github.com/rapid7/metasploit-framework) aiming to focus on real life scenarios and help pentesters all around the world to be able to find peace by providing them all the tools anyone really needs, the Forge is not about working with outdated vulnerabilities that we know won't work, but rather the Forge focuses on actionable vulnerabilities and establishes a standardized methodology for responsible vulnerability disclosure and exploit development within a framework.

## Why this matter?
When starting my career as a pentester and bug hunter I had found that we need a lot of tools, for recoignance, osint, enumeration, exploitation and much more, but what is actually hilarious is the fact that Kali linux or Black Arch does have a lot of tools but no tool that present them all together. Hopefully and perhaps like a dream someday the Kali and BlackArch team will include this inside their built-in tools, but still the goal of this tools is more than engineering all pentesting tools together but actually leveraging the speed for which a pentester developes a ZDE and make a report out of it.

## Code of conduct
Even though the actual extended code of conduct is in [here](./CODE_OF_CONDUCT.md) is important to understand the next lines described below very clear.
* 1st. The Software Developer and contributors of this framework do not make themselves responsible for any wrongdoing resulting on the use of the provided framework.
* 2nd. **Zero-Day Policy**: Do not submit Zero-Day Exploits (ZDEs) as Pull Requests (PRs). Responsible disclosure to the vendor must be completed before any related exploit code can be considered for inclusion. Use the framework's local testing features for development purposes only.
* 3rd. **ANY** pentesting activity and exploitation of **ANY** vulnerability on unauthorized area is considered to be **ILLEGAL** and can be subjected to legal actions against yourself, avoid taking unnecessary risks, for that purpose we provide playgrounds and for real life jobs you can find in the Forge website references to bounty programs like HackerOne, Google or Meta bounty programs.

## Install
```sh
pip install cveforge
cveforge --help
cveforge echo hello there
cveforge # to run interactively
```

## Quickstart

**NOTE: This is a TODO meaning is YET to be implemented**
```sh
uv init # helps you to work in a virtualenv
uv add cveforge # add the cveforge dependency
uv run cveforge scaffold payload --verbose-name WannaCry # add to the forge DB the path to the current project
uv run cveforge scaffold exploit --verbose-name "RSA Cracking" --cve-name cve_2025_0002 # add to the forge DB the path to the current project
uv run cveforge scaffold command --verbose-name "sftp" # add to the forge DB the path to the current project
uv run cveforge # now whenever we modify the payload, the exploit or the command project the cveforge self-refresh
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

### The command entrypoint
```py
from cveforge import tcve_command
from cveforge import Context
import typer
import logging


@tcve_command()
def your_command_name(my_flag: str = typer.Argument()): # WE NOW SUPPORT TYPER!!!
    context: Context = Context() # store general program data
    logging.info("Running your command with flag '%s'", my_flag)
```

### Usage:
```sh
your_command_name "CVE Forge is amazing!!!" # output: info: Running your command with flag 'CVE Forge is amazing!!!'
```

## Developing an Exploit or PoC for CVEs

Developing an exploit is just like creating a command but rather than using the @tcve_command we use the @tcve_exploit like follows:

```py
from cveforge import tcve_exploit

@tcve_exploit(categories=["cve", "privilege escalation"])
def exploit_name(**kwargs):
    pass
```
Note the categories is also a possible command for the @tcve_command decorator, is useful for allowing the user to search with different queries for your command

## FIXME: Known Bugs
1. Cannot open two instances at the same time, even if not intended a more user friendly behavior should be implemented