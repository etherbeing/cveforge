import logging
from typing import Any
from unittest import TestCase

from cveforge.core.context import Context
from cveforge.utils.graphic import get_banner


class GraphicTestCase(TestCase):
    def setUp(self, *args: Any, **kwargs: Any):
        logging.basicConfig(level=logging.DEBUG, force=True)
        self._context = Context()
        return super().setUp()

    def test_get_banner(
        self,
    ):
        """Test obtaining the banner does work"""
        banner = get_banner(context=self._context)
        logging.debug(banner)
        self.assertIsNotNone(banner)