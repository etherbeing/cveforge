import json
import os
from pathlib import Path
from typing import Any, Optional, cast
from typing_extensions import Annotated
from urllib.parse import ParseResult, urljoin, urlparse

from bs4 import BeautifulSoup
from requests import request
import typer

from cveforge.core.commands.run import tcve_command
from cveforge.core.context import Context

@tcve_command()
def download(
    url: str = typer.Argument(),
    types: Annotated[Optional[list[str]], typer.Option()] = None,
    http_method: str = typer.Option(),
    headers: Annotated[Optional[dict[str, Any]], typer.Option(parser=json.loads)] = None,
    output: str | None = typer.Option(),
    recursive: bool = typer.Option(),
    root_paths: Annotated[Optional[list[str]], typer.Option()] = None,
    page_range: Annotated[Optional[list[int]], typer.Option()] = None,
    pages: Annotated[Optional[list[int]],  typer.Option()] = None,
    html_tag_types: Annotated[Optional[list[str]], typer.Option()] = None,
    html_tag_attr: Annotated[Optional[list[str]], typer.Option(help="For example src, data-src and so on")] = None,
    coexist: bool=typer.Option(default=False),
):
    """
Downloading all images from the given website from page 2 to page 4 
download https://wallpapers.com/anonymous/?p={page} --page-range 2 4 --types png jpg -r -P /wallpapers/ /images/ -o ~/Pictures/wallpapers/ -HTT img -H
TA src data-src --coexist
    """
    context = Context()
    html_tag_types = html_tag_types or []
    html_tag_attr = html_tag_attr or []
    if page_range:
        prange = range(page_range[0], page_range[1] + 1)
    elif pages:
        prange = pages
    else:
        prange = None
    if prange:
        for p in prange:
            download(
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
                coexist=coexist,
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
        path_output = Path(output).absolute()  # solve it to be absolute
    else:
        path_output = Path.cwd() / Path(url.split("?")[0]).name

    if path_output.exists() and os.listdir(path_output) and not coexist:
        raise ValueError("Output dir is not empty, please select a new one")

    path_output.mkdir(exist_ok=True)

    for tag_type in html_tag_types:
        for link in cast(list[dict[str, Any]], soup.find_all(tag_type, recursive=True)):
            for attr in html_tag_attr:
                src: ParseResult = cast(ParseResult, urlparse(link.get(attr, "")))
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
                    if not (path_output / src_name).exists():
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
            download(
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
                coexist=coexist,
            )
