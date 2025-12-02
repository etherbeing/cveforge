NULL_BYTE_TOKEN = b"^NULL_BYTE^"
NULL_BYTE = b"\x00"

def cve_format(command: str) -> bytes:
    return command.encode().replace(NULL_BYTE_TOKEN, NULL_BYTE)
