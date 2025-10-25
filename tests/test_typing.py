import logging
import sys
from unittest import TestCase, skipIf

from core.commands.database.initialize import load_cves


class TypingTestCase(TestCase):
    def setUp(self, *args: Any, **kwargs: Any):
        logging.basicConfig(level=logging.DEBUG)
        return super().setUp()

    @skipIf(
        "test_typing_cve" not in sys.argv,
        "Skipped long run test as it is only available when called explicilty",
    )
    def test_typing_cve(self):
        for cve in load_cves():
            pass
