# Example usage: http https://postman-echo.com/get?foo=bar
from http import HTTPMethod
import json
from typing import Annotated, Literal, Optional
import requests
import typer
from cveforge import Context

from cveforge.core.commands.executables.owasp.utils import (
    get_cookies,
    get_files,
    get_headers,
)
from cveforge.core.commands.run import tcve_command


@tcve_command()
def http(
    target: str = typer.Argument(),
    headers: Annotated[Optional[list[str]], typer.Option("-H", "--header")] = None,
    cookies: Annotated[Optional[str], typer.Option("-b", "--cookies")] = None,
    files: Annotated[Optional[list[str]], typer.Option("-f", "--file")] = None,
    method: Annotated[
        Literal[
            HTTPMethod.POST,
            HTTPMethod.PATCH,
            HTTPMethod.CONNECT,
            HTTPMethod.DELETE,
            HTTPMethod.GET,
            HTTPMethod.TRACE,
            HTTPMethod.HEAD,
            HTTPMethod.OPTIONS,
        ],
        typer.Option(
            "-X",
            "--method",
        ),
    ] = HTTPMethod.GET,
    timeout: float = typer.Option(10, "-t", "--timeout"),
    allow_redirects: bool = typer.Option(True, "-r", "--allow-redirects"),
    proxy: Optional[str] = typer.Option(None, "-p", "--proxy"),
    data: Optional[str] = typer.Option(None, "-d", "--data"),
    json_data: Optional[str] = typer.Option(None, "-j", "--json"),
    silent: bool = typer.Option(False)
):
    response = requests.request(
        method,
        target,
        headers=get_headers(headers),
        cookies=get_cookies(cookies),
        files=get_files(files),
        timeout=timeout,
        allow_redirects=allow_redirects,
        proxies={"http": proxy, "https": proxy} if proxy else None,
        data=data,
        json=json.loads(json_data) if json_data else None,
    )
    if not silent:
        if response.headers.get("Content-Type", "").startswith("application/json"):
            Context().stdout.print_json(response.text)
        else:
            Context().stdout.print(response.text)
