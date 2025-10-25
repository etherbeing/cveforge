import json
import logging
from pathlib import Path
from typing import Any, Optional, cast

from core.commands.python.types import Package, VersionedPackage

logging.debug("Initializing python related commands...")


class CacheStorage:
    packages: dict[str, Any] = {}
    local_cache_repo: Path
    packages_file: Path

    def __init__(self, cache_path: Path, packages_file: str) -> None:
        self.local_cache_repo = cache_path
        self.local_cache_repo.mkdir(exist_ok=True, parents=True)
        self.packages_file = self.local_cache_repo / packages_file
        self.packages_file.touch()

    def store_search_results(self, package_name: str, desired_package: Any):
        self.packages[package_name] = desired_package
        with self.packages_file.open("w") as file:
            file.write(json.dumps(self.packages))
        assert (
            self.packages_file.exists()
        ), "Something went wrong while creating the cache file"
        logging.debug("Written file to %s", self.packages_file)

    def get_packages(self, package_name: Optional[str] = None):
        if not self.packages:
            packages_content = self.packages_file.read_bytes()
            if packages_content:
                self.packages = json.loads(packages_content)
            else:
                self.packages = {}
        if package_name:
            return cast(Package, self.packages.get(package_name, None))
        else:
            return cast(VersionedPackage, self.packages)
