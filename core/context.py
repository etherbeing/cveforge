"""
Handle global context for the current user, target host, port, arguments passed to the cli etc...
"""

from argparse import ArgumentParser
import os
from pathlib import Path
import platform


class Args(ArgumentParser):
    "Handle program arguments"


class Context:
    "Store all the settings and anything that is needed to be used global"

    def __new__(cls):
        cls._cached_instance = getattr(cls, "_cached_instance", super().__new__(cls))
        return cls._cached_instance

    def __init__(self):
        if platform.system() == "Windows":
            self.data_dir = Path(
                os.getenv("APPDATA", os.path.expanduser("~\\AppData\\Roaming\\"))
            )
        elif platform.system() == "Darwin":  # macOS
            self.data_dir = Path(os.path.expanduser("~/Library/Application Support/"))
        else:  # Linux and other UNIX-like OS
            self.data_dir = Path(os.path.expanduser("~/.local/share/"))
        self.data_dir = (self.data_dir / Context.SOFTWARE_NAME).absolute()
        self.db_path = self.data_dir / Context.DB_NAME
        self.db_path = self.db_path.absolute()
        base_dir = self.db_path.parent
        base_dir.mkdir(parents=True, exist_ok=True)
        self.db_path.touch(exist_ok=True)
        assert self.db_path.exists()
        self.db_uri = f"sqlite:///{self.db_path}"
        self.history_path = self.data_dir / ".history.cve"

    SOFTWARE_NAME = "CVE Forge"
    BASE_DIR = Path(__file__).parent.parent
    ASSETS_DIR = BASE_DIR / "assets"
    ASSETS_BASE_URL = "assets"
    TEXT_ART_DIR = ASSETS_DIR / "text_art"
    DB_NAME = "data/db.sqlite"
    CVE_FOLDER = ASSETS_DIR / "cvelistv5/cves"
    EC_RELOAD = 3000
    SYSTEM_COMMAND_TOKEN = "@"
    MEDIA_FOLDER = ASSETS_DIR / "data/media"
    CVE_IGNORE_PATH = BASE_DIR / ".cveignore"
    SOFTWARE_SCHEMA_PATH = BASE_DIR / ".cveschema.json"

    # Dynamic data needs class instantiation
    data_dir = None
    DB_ENGINE = "sqlite"
    DB_URI: str
    db_path: Path
    history_path: Path