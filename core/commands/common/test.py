import logging
from argparse import Namespace
from typing import Any, override

from core.commands.run import tcve_command
from core.compression.ber import TheoryTesterFunction
from core.compression.power import BER
from core.context import Context
from core.cryptography.rsa.play import RSA
from utils.args import ForgeParser


class command_parser(ForgeParser):
    @override
    def setUp(self, *args: Any, **kwargs: Any) -> None:
        subparsers = self.add_subparsers(
            dest="option",
        )
        subparsers.add_parser(
            "RSA",
        )
        subparsers.add_parser(
            "BER",
        )
        subparsers.add_parser(
            "NBER",
        )


@tcve_command("test", parser=command_parser)
def command(namespace: Namespace, context: Context):
    logging.debug("Testing %s option", namespace.option)
    if namespace.option == "RSA":
        RSA.test()
    elif namespace.option == "BER":
        BER.test()
    elif namespace.option == "NBER":
        TheoryTesterFunction.test()
