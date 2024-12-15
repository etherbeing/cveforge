import json
import multiprocessing
import os
from pathlib import Path
import pathspec
import hashlib
from pathspec.patterns import GitWildMatchPattern
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from core.context import Context
from core.io import OUT


class Watcher(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()
        self.observer = Observer()
        self.reload = False
        self.pathspec = self.parse_gitignore()
        self.generate_folder_schema()

    def get_file_integrity(self, file_path: Path):
        md5 = hashlib.md5()
        md5.update(file_path.read_bytes())
        return md5.hexdigest()

    def generate_folder_schema(self):
        root = Path(Context.BASE_DIR)
        schema = {}
        cwd = None
        OUT.print("Generating software schema, please wait...")
        for step in root.walk(True, follow_symlinks=False):
            if self.is_path_ignored(step[0]):
                continue
            OUT.print(f"Analyzing folder {step[0]}")
            schema[cwd] = {}
            for file in step[2]:
                file = step[0] / file
                if self.is_path_ignored(file):
                    continue
                schema[cwd][file] = self.get_file_integrity(file)
        with open(Context.SOFTWARE_SCHEMA_PATH, "wb") as schema_file:
            json.dump(schema, schema_file) # type: ignore
        print(schema.__str__())
        return schema

    def parse_gitignore(
        self,
    ):
        """Generate the pathspec from the git file"""
        with open(Context.CVE_IGNORE_PATH, "r", encoding="utf-8") as cveignore:
            return pathspec.PathSpec.from_lines(GitWildMatchPattern, cveignore)

    def is_path_ignored(self, path: Path):
        """Is file ignored by git?"""
        path = path.relative_to(Context.BASE_DIR)
        return self.pathspec.match_file(path)

    def do_reload(self, event: FileSystemEvent, child: multiprocessing.Process):
        if not child or event.is_directory or self.is_path_ignored(Path(str(event.src_path))):
            return
        return # DO NOT RELOAD YET
        OUT.print(
            f"File touched at {event.src_path}, reloading to have latest changes running..."
        )
        self.reload = True
        child.kill()

    def live_reload(self, event: FileSystemEvent):
        """
        Holder to make a bridge to actually reload substitute this file with do_reload and lambda
        """
        pass

    def on_modified(self, event: FileSystemEvent):
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
