def get_headers(args: list[str] | None):
    res: dict[str, str] = {}
    if args:
        for header in args:
            key, value = header.split(":", 1)
            res[key.strip()] = value.strip()
        return res
    else:
        return res


def get_cookies(cookie_str: str | None) -> dict[str, str]:
    if cookie_str:
        return dict([cookie.strip().split("=", 1) for cookie in cookie_str.split(";")])
    else:
        return {}


def get_files(files: list[str] | None) -> dict[str, str]:
    if files:
        res: dict[str, str] = {}
        for file in files:
            res[file] = file
        return res
    else:
        return {}
