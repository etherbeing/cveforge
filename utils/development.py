import hashlib
import json
import logging
from functools import lru_cache
from pathlib import Path
from threading import Thread

import pathspec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern
from watchdog.events import FileModifiedEvent, FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from prompt_toolkit.application.current import get_app_or_none

from core.context import Context
from core.exceptions.ipc import ForgeException
from core.io import OUT
from utils.locking import FileRecordLocking


class Watcher(FileSystemEventHandler):
    """Class that handle live reload and more stuff related to development"""

    def __init__(self, context: Context) -> None:  # type: ignore
        super().__init__()
        self.observer = Observer()
        self.observer.name = "Live Reload Watcher"
        self.context = context
        self.pathspec = self.parse_gitignore()
        self.generate_folder_schema()

    def get_file_integrity(self, file_path: Path):
        """
        Get the sha256 hash of the file
        """
        try:
            sha256 = hashlib.sha256(file_path.read_bytes(), usedforsecurity=False)
        except FileNotFoundError:
            return None
        except Exception as e:
            raise ForgeException() from e
        return sha256.hexdigest()

    @lru_cache
    def generate_folder_schema(self):
        """
        Generate a schema of the software folder to keep track of the files
        """
        with FileRecordLocking(self.context.SOFTWARE_SCHEMA_PATH):
            root = Path(self.context.BASE_DIR)
            schema: dict[str, dict[str, str]] = {}
            OUT.print(
                "Generating software schema, please wait...",
                justify="center",
                width=OUT.width,
            )
            for step in root.walk(True, follow_symlinks=False):
                if self.is_path_ignored(step[0]):
                    continue
                schema[str(step[0])] = {}
                for file in step[2]:
                    file = step[0] / file
                    if self.is_path_ignored(file):
                        continue
                    file_integrity = self.get_file_integrity(file)
                    if not file_integrity:
                        del schema[str(step[0])][file.name]
                        continue
                    else:
                        schema[str(step[0])][file.name] = file_integrity
            with open(self.context.SOFTWARE_SCHEMA_PATH, "wb") as schema_file:
                schema_file.write(
                    json.dumps(schema, indent=4, sort_keys=True).encode("UTF-8")
                )

            OUT.print(
                "Folder schema is generated and ready to be used",
                justify="center",
                width=OUT.width,
            )
            return schema

    @lru_cache  # this is to avoid reading the disk every time
    def get_schema(
        self,
    ):
        with open(self.context.SOFTWARE_SCHEMA_PATH, "rb") as schema_file:
            return json.loads(schema_file.read())

    def update_schema(self, file: Path):
        """Update the given file path schema in the project integrity schema"""
        with FileRecordLocking(self.context.SOFTWARE_SCHEMA_PATH):
            schema = self.generate_folder_schema()
            with open(self.context.SOFTWARE_SCHEMA_PATH, "wb") as schema_file:
                schema_file.truncate(0)
                if str(file.parent) not in schema:
                    schema[str(file.parent)] = {}
                file_integrity = self.get_file_integrity(file)
                if not file_integrity:
                    del schema[str(file.parent)][file.name]
                else:
                    schema[str(file.parent)][file.name] = file_integrity
                schema_file.write(json.dumps(schema, indent=4, sort_keys=True).encode())

    def parse_gitignore(
        self,
    ):
        """Generate the pathspec from the git file"""
        with open(self.context.CVE_IGNORE_PATH, "r", encoding="utf-8") as cveignore:
            return pathspec.PathSpec.from_lines(GitWildMatchPattern, cveignore)

    def is_path_ignored(self, path: Path):
        """Is file ignored by git?"""
        if path == self.context.SOFTWARE_SCHEMA_PATH:
            return True
        if path.name[-3:] != ".py":  # just process the files that are python files
            return True
        path = path.relative_to(self.context.BASE_DIR)
        return self.pathspec.match_file(path)

    def do_reload(self, event: FileSystemEvent, child: Thread):
        """Trigger the reload"""
        trigger_path = Path(str(event.src_path))
        if not child or event.is_directory or self.is_path_ignored(trigger_path):
            return
        previous_id = (
            self.get_schema()
            .get(str(trigger_path.parent), {})
            .get(trigger_path.name, None)
        )
        current_id = self.get_file_integrity(trigger_path)
        if current_id == previous_id:
            return
        self.get_schema.cache_clear()
        self.update_schema(trigger_path)
        OUT.print(
            f"\n\nFile touched at {event.src_path}, reloading to have latest changes running...",
            justify="center",
            width=OUT.width,
        )
        logging.debug("Waiting for prompt thread to be ended gratefully...")
        app = get_app_or_none()
        if app:
            app.exit(exception=ForgeException(code=self.context.EC_RELOAD))
        # self.context.console_session.input.close()
        # self.context.console_session.app.exit()
        # self.context.console_session.app.invalidate()
        child.join()
        # TODO Deterministically make it so the main thread or prompt thread is actually reloaded

    def live_reload(self, event: FileSystemEvent):
        """
        Holder to make a bridge to actually reload substitute this file with do_reload and lambda
        """

    def on_modified(self, event: FileSystemEvent):
        if type(event) is FileModifiedEvent:
            self.live_reload(event)

    def on_created(self, event: FileSystemEvent):
        self.live_reload(event)

    def on_deleted(self, event: FileSystemEvent):
        self.live_reload(event)

    def start(self, watch_folder: Path):
        watcher = self.observer.schedule(
            self, str(watch_folder), recursive=True
        )  # Set recursive=False to watch only the top directory.
        self.observer.start()
        return watcher

    def stop(
        self,
    ):
        self.observer.stop()

    def join(self):
        self.observer.join()
