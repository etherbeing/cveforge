import argparse
import subprocess
import sys
from typing import TextIO
from utils.args import ForgeParser


class Parser(ForgeParser):
    add_help = False
    def setUp(self) -> None:
        self.add_argument("params", nargs=argparse.REMAINDER, default=[])
    
    def print_usage(self, file: TextIO|None=None): # pyright: ignore[reportIncompatibleMethodOverride]
        if file is None:
            file = sys.stdout
        subprocess.call([self.prog, "--help"], stdout=file)

    def print_help(self, file: TextIO|None=None): # pyright: ignore[reportIncompatibleMethodOverride]
        if file is None:
            file = sys.stdout
        subprocess.call([self.prog, "--help"], stdout=file)