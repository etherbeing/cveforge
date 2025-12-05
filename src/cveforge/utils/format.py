from abc import abstractmethod
import re
from typing import Any, Generator, Optional
from django.utils.translation import gettext as _
import wordlist

LOWER_CHARSET = "abcdefghijklmnopqrstuvwxyz"
UPPER_CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
NUMERIC_CHARSET = "0123456789"
SPECIAL_CHARSET = "~!?><`,./;':{}[]|\\+=_-"
DEFAULT_CHARSET = LOWER_CHARSET + UPPER_CHARSET + NUMERIC_CHARSET
CVE_TOKEN_SEP = "^"


def to_cve_token(name: str):
    return CVE_TOKEN_SEP + name + CVE_TOKEN_SEP


class _None:
    pass


class CVEToken:
    _static_state: Optional[Generator[Any, Any, Any]] = None

    @property
    def has_static_state(self):
        return self._static_state is not None

    def __init__(
        self,
        name: str,
        params: Optional[dict[str, type]] = None,
        default: Optional[Any] = None,
    ) -> None:
        self._name = name
        self._params = params
        self._default = default

    def __str__(self) -> str:
        return f"{self._name}{(':' + ','.join(self._params.keys())) if self._params else ''}"

    def compile(self, value: str):
        """
        Given the input value it determines the token parameters value and defaults

        :param value: The CVE string to compile containing or not the tokens, if no token given then it returns the string as it is
        :type value: str
        """
        cve_token_format = self.format.__annotations__
        format_kwargs: dict[str, Any] = {}

        tokens = re.search(rf"\^{self._name}(:.+)?\^", value)

        if not tokens:
            return None  # no tokens found return the value as it is

        g = tokens.group(0).strip(CVE_TOKEN_SEP)
        gs = tokens.regs[0][0]
        gt = tokens.regs[0][1]
        params = g.split(":")[1]
        complex = re.search(r"[\",]", params)
        if not complex:
            format_kwargs[list(cve_token_format.keys())[0]] = params
            t = self.format(**format_kwargs)
            if isinstance(t, Generator):
                try:
                    value = value[0:gs] + next(t) + value[gt:]
                except RuntimeError:
                    CVEToken._static_state = None
                    return None
            else:
                value = value[0:gs] + t + value[gt:]
            return value
        remaining = params.strip()
        while len(
            remaining
        ):  # this is formatting the parameters to call the format function
            t = remaining.split("=", 1)
            param_name = t[0]
            if len(t) > 1:
                remaining = t[1]
            else:
                remaining = ""
            param_name = param_name.strip()
            remaining = (
                remaining.lstrip()
            )  # just focus on the left side as the right side is already stripped

            param_type = cve_token_format.get(param_name, _None)
            if param_type is _None:
                raise AttributeError(
                    _("Given parameter doesn't seems to exist for the given token")
                )
            param_value: Any = None
            if issubclass(param_type, str):
                assert remaining.startswith('"'), _(
                    '%s is of type %s so it must start with a "'
                    % (param_name, param_type)
                )
                remaining = remaining.lstrip(
                    '"'
                )  # we need to go towards the next " which is not escaped
                param_value = ""
                for i, character in enumerate(
                    remaining
                ):  # please note that ^TOKEN:"^"^ The ^ inside the string is not considered end of the token as it is inside the " and we expected a ^ there no need to escape it
                    if (
                        character == '"' and remaining[i - 1] != "\\"
                    ):  # then is not escaped
                        break
                    param_value += character
                else:
                    raise ValueError(
                        _("Unclosed string found")
                    )  # example ^TOKEN:"asd^ as it is invalid
                remaining = (
                    remaining[len(param_value) + 2 :].lstrip().removeprefix(",")
                )  # +2 is due to the two ", removes the , in case there any new param so it works like it is the first one
            elif issubclass(param_type, int):
                t = remaining.split(",", 1)
                param_value = t[0]
                # in integers let's just jump until the next param and parse what we got as the first index
                if len(t) > 1:
                    remaining = t[1]
                else:
                    remaining = ""
                param_value = int(
                    param_value.strip()
                )  # parse the obtained value as an int

            format_kwargs[param_name] = param_value
        formatted = self.format(**format_kwargs)
        if isinstance(formatted, Generator):
            value = value[0:gs] + next(formatted) + value[gt:]
        else:
            value = value[0:gs] + formatted + value[gt:]
        return value

    @abstractmethod
    def format(self, *args: Any, **kwargs: Any) -> str | Generator[Any, str, Any]: ...


class NullByteToken(CVEToken):
    def __init__(self) -> None:
        super().__init__("NULL_BYTE")

    def format(self):
        return "\0"


class RandomToken(CVEToken):
    def __init__(self) -> None:
        super().__init__(
            "RANDOM",
            {
                "min": int,
                "max": int,
            },
            {"min": 1, "max": 10},
        )

    def format(self, pattern: str):
        if not self._static_state:
            self._static_state = wordlist.Generator(
                charset=DEFAULT_CHARSET
            ).generate_with_pattern(pattern=pattern)
        for random in self._static_state:
            yield random
        raise StopIteration()


class CVESyntax:
    _tokens: list[CVEToken] = []

    @property
    def has_variant(self):
        for token in self._tokens:
            if token.has_static_state:
                return True
        return False

    def __init__(self, value: str) -> None:
        self._value = value
        self._tokens = [RandomToken(), NullByteToken()]
        self._formatted_value: str = value

    def process(self) -> str:
        for token in self._tokens:
            if t := token.compile(self._formatted_value):
                self._formatted_value = t
        return self._formatted_value

    def __str__(self) -> str:
        return self.process()

    def __iter__(
        self,
    ):
        touched = False
        for token in self._tokens:
            try:
                while (
                    r := token.compile(self._formatted_value)
                ):  # should rise StopIteration when the generator is consumed and stop this (perhaps?)
                    if not r:  # means or the value didn't change from last execution meaning is stuck or the value didn't change at all then
                        break
                    touched = True
                    yield r
            except StopIteration:
                continue
        if not touched:
            yield self._formatted_value
        else:
            yield None

    async def __aiter__(self):
        touched = False
        for token in self._tokens:
            try:
                while (
                    r := token.compile(self._formatted_value)
                ):  # should rise StopIteration when the generator is consumed and stop this (perhaps?)
                    if not r:  # means or the value didn't change from last execution meaning is stuck or the value didn't change at all then
                        break
                    touched = True
                    yield r
            except StopIteration:
                continue
        if not touched:
            yield self._formatted_value
        else:
            yield None


def cve_format(command: str) -> CVESyntax:
    """
    Format a given string into a cve usage general content, helpful for operations that uses the same general content
    Syntax:
        ^TOKEN:<params>^
    Tokens:
        RANDOM[pattern,min,max]: Generates a random value with the optional given value

    :param command: Description
    :type command: str
    :return: Description
    :rtype: bytes
    """
    return CVESyntax(command)
