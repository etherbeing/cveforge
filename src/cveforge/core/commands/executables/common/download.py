import json
import os
from http import HTTPMethod
from pathlib import Path
from typing import Any, cast
from urllib.parse import ParseResult, urljoin, urlparse

from bs4 import BeautifulSoup
from requests import request

from core.commands.run import tcve_command
from core.context import Context
from utils.args import ForgeParser


class DownloadParser(ForgeParser):
    usage = """
Downloading all images from the given website from page 2 to page 4 
download https://wallpapers.com/anonymous/?p={page} --page-range 2 4 --types png jpg -r -P /wallpapers/ /images/ -o ~/Pictures/wallpapers/ -HTT img -H
TA src data-src --coexist
"""
    def setUp(self, *args: Any, **kwargs: Any) -> None:
        self.add_argument(
            "url",
        )
        self.add_argument(
            "--types",
            "-t",
            nargs="+",
            help="List of file types to filter",
            required=False,
            default=None,
        )
        self.add_argument(
            "--http-method",
            "-m",
            default=HTTPMethod.GET,
            choices=[HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH],
        )
        self.add_argument("--headers", "-H", required=False, type=json.loads)
        self.add_argument(
            "--output",
            "-o",
            default=None,
            help="Output dir to download files to, if not set defaults to current working dir",
        )
        self.add_argument("--recursive", "-r", default=False, action="store_true")
        self.add_argument(
            "--root-paths",
            "-P",
            default=None,
            required=False,
            nargs="+",
            help="The path where to root the downloads no downloads will be made outside this path, defaults to the url given path, use / for a more broad path",
        )
        self.add_argument("--page-range", nargs=2, required=False, default=None, type=int)
        self.add_argument("--pages", nargs="+", type=int)
        self.add_argument("--html-tag-types", "-HTT", nargs="+", type=str, required=True, help="For example img, video, picture and so on")
        self.add_argument("--html-tag-attr", "-HTA", nargs="+", type=str, required=True, help="For example src, data-src and so on")
        self.add_argument("--coexist", "-c", help="Makes both the files to be downloaded and the existing file on an output dir to coexist (defaults False)", action="store_true", default=False)

@tcve_command("download", parser=DownloadParser)
def download_command(
    context: Context,
    url: str,
    types: list[str],
    http_method: str,
    headers: dict[str, Any],
    output: str | None,
    recursive: bool,
    root_paths: list[str] | None,
    page_range: list[int],
    pages: list[int],
    html_tag_types: list[str],
    html_tag_attr: list[str],
    coexist: bool,
):
    if page_range:
        prange = range(page_range[0], page_range[1]+1)
    elif pages:
        prange = pages
    else:
        prange = None
    if prange:
        for p in prange:
            download_command(
                context=context,
                url=url.format(page=p),
                types=types,
                http_method=http_method,
                headers=headers,
                output=output,
                recursive=recursive,
                root_paths=root_paths,
                page_range=None,
                pages=None,
                html_tag_types=html_tag_types,
                html_tag_attr=html_tag_attr,
                coexist=coexist
            )
        return
    response = request(http_method, url, headers=headers)
    response.raise_for_status()
    url_parsed = urlparse(
        url,
    )
    root_paths = root_paths or [url_parsed.path]
    if not url_parsed.hostname:
        raise ValueError(
            "No origin provided, please make sure the URL is well formatted"
        )
    url_scheme = url_parsed.scheme or "https"

    soup = BeautifulSoup(response.text, "html.parser")

    if output:
        path_output = Path(output).absolute() # solve it to be absolute
    else:
        path_output = Path.cwd() / Path(url.split("?")[0]).name

    if path_output.exists() and os.listdir(path_output) and not coexist:
        raise ValueError("Output dir is not empty, please select a new one")

    path_output.mkdir(exist_ok=True)
    
    for tag_type in html_tag_types:
        for link in cast(list[dict[str, Any]], soup.find_all(tag_type, recursive=True)):
            for attr in html_tag_attr:
                src: ParseResult = cast(
                    ParseResult, urlparse(link.get(attr, ""))
                )
                scheme: str = cast(str | None, src.scheme) or url_scheme  # type: ignore
                hostname: str = cast(str | None, src.hostname) or url_parsed.hostname  # type: ignore

                target_url: str = urljoin(f"{scheme}://{hostname}", src.path)

                src_name = Path(src.path.split("?")[0]).name
                should_fetch = False
                if not types:  # means all files
                    should_fetch = True
                else:
                    src_ext = src_name.split(".")[-1]
                    if src_ext in types:
                        should_fetch = True
                if should_fetch:
                    img_data = request(http_method, target_url).content
                    if not (path_output/src_name).exists():
                        with open(path_output / src_name, "xb") as f:
                            f.write(img_data)
                            break
                    else:
                        break
                else:
                    continue

    # Recurse through links
    for link in cast(list[dict[str, Any]], soup.find_all("a", recursive=True)):
        href: ParseResult = urlparse(str(link.get("href")))

        scheme: str = cast(str | None, href.scheme) or url_scheme  # type: ignore
        hostname: str = cast(str | None, href.hostname) or url_parsed.hostname  # type: ignore

        if url_parsed.hostname == hostname and any(
            map(lambda root_path: href.path.startswith(root_path), root_paths)
        ):  # if is an allowed subpath
            next_url = urljoin(f"{scheme}://{hostname}", href.path)
            download_command(
                context=context,
                url=next_url,
                types=types,
                http_method=http_method,
                headers=headers,
                output=output,
                recursive=recursive,
                root_paths=root_paths,
                page_range=None,
                pages=None,
                html_tag_types=html_tag_types,
                html_tag_attr=html_tag_attr,
                coexist=coexist
            )
