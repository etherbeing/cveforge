from pathlib import Path
from typing import Any

from utils.args import ForgeParser


class NetcatParser(ForgeParser):
    def setUp(self, *args: Any, **kwargs: Any) -> None:
        self.add_argument("--port", "-p", type=int, required=True)
        self.add_argument("--buffer", "-b", type=int, default=4096)
        self.add_argument("--timeout", "-T", type=int, default=60)
        self.add_argument("--foreground", "-F", action="store_true", default=False)
        self.add_argument("--command", "-c")
        self.add_argument("--upload", "-u")
        self.add_argument("--listen", "-l", default="0.0.0.0")
        self.add_argument("--execute", "-e", type=Path)
        self.add_argument("--target", "-t")
        self.add_argument("--upload-path", "-U", type=Path)
