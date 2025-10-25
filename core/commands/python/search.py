import logging
import re
from argparse import Namespace
from typing import Optional, cast

import requests
import xmltodict
from packaging.version import Version

from core.commands.python import CacheStorage
from core.commands.python.types import Package, VersionedPackage
from core.io import OUT


def pip_search(
    namespace: Namespace, storage: CacheStorage, is_verbose: bool = False
) -> Package:
    """
    TODO Using the cache folder .pipenvs store the search request dictionary for further access on offline mode
    TODO Implement the functionalities missing
    """
    if is_verbose:
        message = """
Package Name: {package}
Package Size: {size}
Metadata Cached: {mcached}
Package Cached: {cached}
Versions: {versions}
"""
    else:
        message = ""
    if not namespace.package:
        raise ValueError("You must provide a package name in order to use this option")
    package = namespace.package.split("==", 1)
    version: Optional[str] = None
    if len(package) > 1:
        version = package[1]
    package = package[0]
    if not namespace.ignore_cache:
        cached_package = storage.get_packages(package)
        if cached_package:
            if version:
                cached_package = cached_package.get(version, None)
            if cached_package:
                logging.debug("Fetching %s from cache", package)
                logging.debug("Content retrieved %s", cached_package)
                OUT.print(
                    message.format(
                        package=package,
                        size=0,
                        mcached=True,
                        cached=False,
                        versions=[version for version in cached_package],
                    )
                )
                return cast(Package, list(cached_package.values())[0])
    for i in range(namespace.retries):
        try:
            html_content = requests.get(
                f"https://pypi.org/simple/{package}/", timeout=namespace.timeout
            )
            break
        except requests.Timeout:
            OUT.print(f"[red]Attempt #{i+1} to download the file, failed[/red]")
    else:
        raise TimeoutError(
            f"Timeout reached {namespace.retries} times and no full content could be downloaded, please try again to resume"
        )
    versions = re.findall("<a.+>.*</a>", html_content.text)
    packages: dict[str, VersionedPackage] = {package: {}}  # useful for caching after
    desired_package: Package = {"remote_url": "", "wheel_url": ""}
    for a in versions:
        raw_remote_package = xmltodict.parse(a)
        raw_remote_package: dict[str, str] = raw_remote_package.get(
            "a",
        )  # type: ignore as this will always be
        package_name = raw_remote_package.pop("#text")
        remote_url = raw_remote_package.pop("@href")
        package_version = re.match(r"[\d\.]{1,4}[\d]", package_name.split("-", 1)[1])
        if not package_version:
            continue  # refusing to work with a package with no version
        else:
            package_version = package_version.group()

        remote_package: Package = packages[package].get(
            package_version, {"remote_url": "", "wheel_url": ""}
        )
        if package_name.endswith(".whl"):
            remote_package["wheel_url"] = remote_url
        elif package_name.endswith(".tar.gz"):
            remote_package["remote_url"] = remote_url
        if not package_name:
            logging.warning("Something wrong with the decodification")
            continue
        packages[package][package_version] = remote_package
        if version == package_version:
            desired_package = remote_package
    if not version:
        version = str(max([Version(version) for version in packages[package]]))
        desired_package = packages[package][version]

    storage.store_search_results(package, desired_package={version: desired_package})

    OUT.print(
        message.format(
            package=package,
            size=0,
            mcached=False,
            cached=False,
            versions=[version for version in packages[package]],
        )
    )
    return desired_package
