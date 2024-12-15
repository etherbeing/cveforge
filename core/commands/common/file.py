from argparse import ArgumentParser, Namespace
from pathlib import Path

from core.commands.security.hackthebox.certified import pol_reader, pol_reader_parser
class command_open_parser(ArgumentParser):
    file: str
    def __init__(self, *args, **kwargs): # type: ignore
        super().__init__(*args, **kwargs) # type: ignore
        self.add_argument("file")

def get_type(instance: Namespace ):
    parts: list[str] = instance.file[::-1].split(".", 1)
    if not (len(parts) > 1):
        return None # as there is no extension in the file TODO implement a way to obtain the file type by extension
    ext: str = parts[0][::-1] # reverse it again as we alread reversed it before
    # name = parts[1][::-1]
    return ext.lower()

def command_open(namespace: Namespace):
    """
        Handle file open in the CVE Forge context
    """
    file = Path(namespace.file)
    if not file.exists():
        raise FileNotFoundError(f"{namespace.file} does not exist, please check for any typo")
    if get_type(namespace) == "pol":
        return pol_reader(pol_reader_parser().parse_args([namespace.file]))
    else:
        with open(file, mode="rb") as rfile:
            return rfile.read()
