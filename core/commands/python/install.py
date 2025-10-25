import logging
import os
import shutil
import site
import subprocess
import sys
import tarfile
import zipfile
from argparse import Namespace
from pathlib import Path

import requests

from core.commands.python import CacheStorage
from core.commands.python.search import pip_search
from core.commands.python.types import Package
from core.context import Context


def resumable_download(
    url: str, dst_path: str | Path, timeout: int, retries: int, chunk_size: int = 8192
):
    headers: dict[str, str] = {}

    if os.path.exists(dst_path):
        downloaded = os.path.getsize(dst_path)
        headers["Range"] = f"bytes={downloaded}-"
    else:
        downloaded = 0
    for i in range(retries):
        try:
            with requests.get(url, headers=headers, stream=True, timeout=timeout) as r:
                r.raise_for_status()

                total = (
                    int(r.headers.get("Content-Range", "").split("/")[-1])
                    if "Content-Range" in r.headers
                    else int(r.headers.get("Content-Length", 0))
                )
                mode = "ab" if downloaded > 0 else "wb"

                with open(dst_path, mode) as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            print(f"\rDownloaded {downloaded} / {total} bytes", end="")

                logging.info("Package successfully downloaded to path: %s...", dst_path)
                return dst_path
        except Exception as ex:
            logging.debug(
                "Attempt to download the file #%s failed because: %s", i + 1, ex
            )
    else:
        raise Exception(
            "Max amount of retries (%s) reached and the content couldn't be completly downloaded please try again to resume the download."
            % retries
        )


def wheel_install(url: str, timeout: int, retries: int, context: Context):
    name, file_hash = url.split(
        "/",
    )[
        -1
    ].split("#")

    package_dir = context.tmp_dir / name
    package_dir.mkdir(exist_ok=True)

    wheel_path = resumable_download(url, package_dir, retries=retries, timeout=timeout)
    with zipfile.ZipFile(wheel_path, "r") as zip_ref:
        zip_ref.extractall(package_dir)

    site_packages = next(p for p in site.getsitepackages() if os.access(p, os.W_OK))

    for item in os.listdir(package_dir):
        item_path = os.path.join(package_dir, item)
        if os.path.isdir(item_path) and (
            item.endswith(".dist-info")
            or item.endswith(".data")
            or os.path.exists(os.path.join(item_path, "__init__.py"))
        ):
            shutil.copytree(
                item_path, os.path.join(site_packages, item), dirs_exist_ok=True
            )
        elif os.path.isfile(item_path) and item.endswith(".py"):
            shutil.copy2(item_path, os.path.join(site_packages, item))


def source_install(url: str, timeout: int, retries: int, context: Context):
    name, file_hash = url.split(
        "/",
    )[
        -1
    ].split("#")
    package_dir = context.tmp_dir / name
    package_dir.mkdir(exist_ok=True)
    archive_path = resumable_download(url, package_dir, timeout, retries=retries)
    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(package_dir)

    # Find the extracted directory
    extracted_dirs = [
        d
        for d in os.listdir(package_dir)
        if os.path.isdir(os.path.join(package_dir, d))
    ]
    if not extracted_dirs:
        raise Exception("No directory found in tar.gz")
    project_dir = os.path.join(package_dir, extracted_dirs[0])

    # Check for pyproject.toml (PEP 517/518)
    pyproject = Path(project_dir) / "pyproject.toml"
    if pyproject.exists():
        subprocess.check_call([sys.executable, "-m", "pip", "install", "build"])
        subprocess.check_call(
            [sys.executable, "-m", "build", "--wheel"], cwd=project_dir
        )

        # Find built wheel and install it
        dist_dir = Path(project_dir) / "dist"
        wheel_files = list(dist_dir.glob("*.whl"))
        if not wheel_files:
            raise Exception("Wheel build failed")
        wheel_install(
            wheel_files[0].as_uri(), timeout, retries=retries, context=context
        )  # Reuse the function
    else:
        # Fallback: traditional setup.py
        subprocess.check_call([sys.executable, "setup.py", "install"], cwd=project_dir)


def pip_install(namespace: Namespace, storage: CacheStorage, context: Context):
    desired_package: Package = pip_search(namespace, storage=storage, is_verbose=False)
    if namespace.no_wheel:
        remote_url = desired_package.get("remote_url")
        source_install(
            remote_url, namespace.timeout, retries=namespace.retries, context=context
        )
    else:
        remote_url = desired_package.get("wheel_url")
        wheel_install(
            remote_url, namespace.timeout, retries=namespace.retries, context=context
        )
