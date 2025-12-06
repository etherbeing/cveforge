from http import HTTPMethod
import shlex
from typing import Annotated, Any, Literal, Optional

from requests import request
import typer

from cveforge.core.commands.executables.owasp.utils import get_cookies, get_headers
from cveforge.core.commands.run import tcve_command
from cveforge.core.context import Context


def dictionary_value(wordlist: str):
    with open(wordlist, "rb") as file:
        for line in file.readlines():
            yield line.decode().strip()


def process_cve_script(script: str, context: dict[str, Any]):
    """I'm too lazy for tokenization and later processing :-("""
    parts = shlex.split(script)
    values: list[Any] = []

    # substitution
    for token in parts:
        if token == "ok":
            values.append(context["response"].ok)
        elif token == "response":
            values.append(context["response"])
        elif token == "body":
            values.append(context["response"].text)
        elif token == "status":
            values.append(context["response"].status)
        else:
            values.append(token)
    # processing
    results: list[bool | str] = []
    past_token = None
    operation = None
    auxiliar = None
    for token in values:
        if token == "and":
            operation = "and"
        elif token == "is":
            operation = "is"
        elif token == "not":
            auxiliar = "not"
        elif token == "in":
            operation = "in"
        elif token and operation:
            if not past_token:
                raise SyntaxError("Invalid syntax")
            if operation == "is":
                results.append(past_token == token)
            elif operation in ["and", "or"]:
                if auxiliar == "not":
                    results.append(not past_token)
                    auxiliar = None
                else:
                    results.append(past_token)
                results.append(operation)
            elif operation == "in":
                if auxiliar == "not":
                    results.append(past_token not in token)
                    auxiliar = None
                else:
                    results.append(past_token in token)
            operation = None
        else:
            past_token = token
    result = results[0]
    for i in range(1, len(results), 2):
        if results[i] == "and":
            result = result and results[i + 1]
        elif results[i] == "or":
            result = result or results[i + 1]
    return result


@tcve_command()
def brute_force(
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
    ssl_verify: bool = typer.Option(False, "-V", "--verify"),
    expects: Optional[str] = typer.Option(),
    wordlist: Optional[str] = typer.Option(),
):
    """
    This command turns a curl command into a bruteforceable query, tested against DVWA brute_force

    curl 'http://192.168.56.102/dvwa/vulnerabilities/brute/?username={username}&password={password}&Login=Login' \
        -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
        -H 'Accept-Language: en-US,en;q=0.9,es;q=0.8' \
        -H 'Connection: keep-alive' \
        -b 'security=high; PHPSESSID=0f7e06c6c272b7cfeaff704a7ab2c2e5' \
        -H 'Referer: http://192.168.56.102/dvwa/vulnerabilities/brute/' \
        -H 'Upgrade-Insecure-Requests: 1' \
        -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36' \
        --insecure
    Usage:
        Brute force the username and password looking for the return message to not contain the access denied messag e error in the body
        $ brute_force -Q username -Q password --expects="ok and 'Username and/or password incorrect.' not in body "
        $ brute_force -Q username -Q password --expects "'Username and/or password incorrect.' not in body" -W /usr/share/dict/rockyou.txt 
    """
    context = Context()

    # if wordlist:
    #     dict_entry = dictionary_value(wordlist)
    # else:
    #     dict_entry = None
    while True:
        res = request(
            method,
            target,
            headers=get_headers(headers),
            data=data,
            json=json_data,
            cookies=get_cookies(cookies),
            verify=ssl_verify,
        )
        if (
            expects
            and process_cve_script(
                expects, context={"response": res}
            )
            or (not expects and res.ok)
        ):
            context.stdout.print("Cracked")
            break
