from typing import Literal

DIALECT_NAMES = Literal["ntlm", "kerberos"]


class Dialect:
    def __init__(self, content: bytes) -> None:
        self._content = content

    @classmethod
    def name_to_dialect(cls, name: DIALECT_NAMES):
        if name == "ntlm":
            return Dialect(content=b"NT LM 0.12")
        return None

    def to_header(
        self,
    ):
        return b"\x02%b\x00" % self._content
