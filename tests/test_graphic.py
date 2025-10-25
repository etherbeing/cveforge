import logging
from unittest import TestCase

from prompt_toolkit import PromptSession

from utils.graphic import get_banner, rich_to_prompt


class GraphicTestCase(TestCase):
    def setUp(self, *args: Any, **kwargs: Any):
        logging.basicConfig(level=logging.DEBUG)
        return super().setUp()

    def test_get_banner(
        self,
    ):
        """Test obtaining the banner does work"""
        banner = get_banner()
        logging.debug(banner)
        self.assertIsNotNone(banner)

    def test_rich_to_prompt(
        self,
    ):
        rich_text = "[green]Hello world[/green]"
        session = PromptSession()
        session.prompt(rich_to_prompt(rich_text))
