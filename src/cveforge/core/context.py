"""
Handle global context for the current user, target host, port, arguments passed to the cli etc...
"""

import getpass
import logging
import os
import platform
import sys
import threading
from functools import lru_cache
from logging import basicConfig
from pathlib import Path
from types import TracebackType
from typing import Any, Literal, Optional, Self, TypedDict

import typer


from cveforge.core.commands.command_types import TCVECommand

from tomllib import load

from prompt_toolkit import PromptSession

from cveforge.utils.module import load_module_from_path
from rich.console import Console


class CVESession:
    """
    If we should proxify(send requests through an specific place) any request so when we have an opened session commands go to the target session instead this is is the middleware for that
    """

    @property
    def protocol(self):
        return self._protocol

    def __init__(
        self,
        context: "Context",
        protocol: Literal["ssh", "sftp", "local"],
        session_object: Any = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        hostname: Optional[str] = None,
        port: Optional[int] = None,
        path: Optional[str] = None,
    ) -> None:
        self._context = context
        self._protocol = protocol
        self._session_object = session_object
        self._username = username
        self._password = password
        self._hostname = hostname
        self._port = port
        self._path = path

    def __str__(self) -> str:
        formatted_text = ""
        formatted_text += self._protocol + "://"
        if self._username:
            formatted_text += self._username
            if self._password:
                formatted_text += ":" + "*" * 8
        if self._hostname:
            if self._username:
                formatted_text += "@"
            formatted_text += self._hostname
            if self._port:
                formatted_text += ":" + str(self._port)
        if self._path:
            formatted_text += self._path
        return formatted_text

    def run(self, command: TCVECommand, *args: Any, **kwargs: Any):
        return command.get("command").run(self._context, *args, **kwargs)

    def get_session_object(self):
        return self._session_object

    def __bool__(
        self,
    ):
        return self._protocol != "local"


class CommandContext(TypedDict):
    current_command: TCVECommand | None


class Context:
    """Store all the settings and anything that is needed to be used global"""

    _singleton_instance = None
    _lock: threading.Lock = threading.Lock()
    exit_status: int | None = None

    __name__ = "CVE Forge"

    def __new__(cls):
        """Singleton constructor"""
        with cls._lock:
            if cls._singleton_instance is None:
                cls._singleton_instance = super().__new__(
                    cls
                )  # FIXME The web is using a reflection of this context instance for some reason we need it to receive the real Context instead
        return cls._singleton_instance

    def __init__(self):
        logging.debug(
            "Initializing singleton Context instance, only one in the logs of these message should exist"
        )
        threading.main_thread().name = "CVE Forge Executor"

        self.proxy_client: Optional[Any] = None
        self._cli = typer.Typer()

        if platform.system() == "Windows":
            self.data_dir = Path(
                os.getenv("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local\\"))
            )
        elif platform.system() == "Darwin":  # macOS
            self.data_dir = Path(os.path.expanduser("~/Library/Application Support/"))
        else:  # Linux and other UNIX-like OS
            self.data_dir = Path(os.path.expanduser("~/.local/share/"))
        self.data_dir = (
            self.data_dir / self.SOFTWARE_NAME.replace(" ", "_").lower()
        ).absolute()
        self.log_file = self.data_dir / ".cve.{host_id}.log"
        self.tmp_dir = self.data_dir / "tmp"
        self.tmp_dir.mkdir(exist_ok=True, parents=True)
        self.history_path = self.data_dir / ".history.cve"
        self.custom_history_path = self.data_dir / ".histories/"
        logging.info("History file is at: %s", self.history_path)
        self.custom_history_path.mkdir(exist_ok=True, parents=True)
        logging.info("Program data folder is: %s", self.data_dir)
        self.STATIC_DIR.mkdir(mode=0o755, parents=True, exist_ok=True)
        self.MEDIA_DIR.mkdir(mode=0o755, parents=True, exist_ok=True)

    def configure_logging(self, log_level: int):
        """
        Configure python default logger or root logger to store logs in a predetermined place
        """
        self._log_level = log_level
        log_file = str(self.log_file).format(host_id=getpass.getuser())
        self.stdout.print(f"[yellow]Storing logs at: {log_file}[/yellow]")
        Path(log_file).touch(mode=0o755)
        self.setup_fd()  # make sure to get the correct stdout
        basicConfig(
            level=log_level,
            filename=log_file,  # if self.log_to_stdout else log_file,
            filemode="a",  # Use 'a' for appending logs, or 'w' to overwrite
            format=self.LOG_FORMAT,
            datefmt=self.LOG_DATE_FTM,  # Optional: Customize timestamp format
            force=True,
        )
        logging.debug("Logging setup correctly")

    @property
    def cli(self):
        return self._cli

    SOFTWARE_NAME = "CVE Forge"
    BASE_DIR = Path(__file__).parent.parent
    WEB_DIR = BASE_DIR / "web"
    COMMANDS_DIR = BASE_DIR / "core/commands/executables"
    PAYLOAD_DIR = BASE_DIR / "payloads"
    LOG_FILE: Path = (
        BASE_DIR / ".cve.{host_id}.log"
    )  # DeprecationWarning: Use context.log_file instead
    ASSETS_DIR = BASE_DIR / "assets"
    STATIC_DIR = Path("/var/www/html/cveforge/static/")
    MEDIA_DIR = Path("/var/www/html/cveforge/media/")
    TEXT_ART_DIR = ASSETS_DIR / "text_art"
    DEFAULT_CVE_CONFIG_PATH = BASE_DIR / ".cveforge.toml"
    
    # Exception Codes, useful for tree level deep communication
    EC_RELOAD = 3000
    EC_EXIT = 3001
    EC_CONTINUE = 3002
    
    # Return codes, useful for arbitrary exits from the program
    RT_OK = 0
    RT_INVALID_COMMAND = 4000
    RT_ADDRESS_IN_USE = 4001

    SYSTEM_COMMAND_TOKEN = "@"
    CVE_IGNORE_PATH = BASE_DIR / ".cveignore"
    SOFTWARE_SCHEMA_PATH = BASE_DIR / ".cveschema.json"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(funcName)s - %(message)s"
    LOG_DATE_FTM = "%Y-%m-%d %H:%M:%S"

    # Dynamic data needs class instantiation
    data_dir = None
    _web_address = "127.0.0.1:3780"
    history_path: Path
    custom_history_path: Path
    protocol_name: Optional[str] = None

    _console_session: PromptSession[str]

    _command_context: CommandContext = {"current_command": None}

    _log_level: int = logging.INFO

    stdout: Console = Console()
    stdin: Console = Console()
    stderr: Console = Console()

    def set_web_address(self, value: str):
        self._web_address = value # TODO check is valid

    @property
    def web_address(self):
        return self._web_address

    @property
    def log_level(self):
        return self._log_level

    @property
    def console_session(self):
        return getattr(self, "_console_session", PromptSession[str]())

    def setup_fd(self):
        self.stdout = Console(file=sys.stdout)
        self.stderr = Console(file=sys.stderr)
        self.stdin = Console(file=sys.stdin)

    def set_console_session(self, value: PromptSession[str]):
        self._console_session = value

    @property
    def command_context(
        self,
    ):
        """Returns a command related context"""
        return self._command_context

    # cli: PromptSession[str] # Command Line
    # For shared context that needs to be transmitted through multiple commands,
    # (e.g. between network usage)
    network_session: Optional[CVESession] = None

    # trunk-ignore(ruff/B019)
    @lru_cache()
    def get_commands(
        self,
    ):
        from cveforge.core.commands.run import tcve_command

        commands: dict[str, TCVECommand] = {}
        assert self.DEFAULT_CVE_CONFIG_PATH.exists()
        command_paths: list[Path] = [self.COMMANDS_DIR]
        with self.DEFAULT_CVE_CONFIG_PATH.open("rb") as config:
            config_data = load(config)
            toml_commands: list[str] = config_data.get("core", {}).get("commands", [])
            for command_path in toml_commands:
                pt = Path(command_path).expanduser()
                if not pt.is_absolute():
                    command_full_path = (self.BASE_DIR / pt).absolute()  # normalize it
                else:
                    command_full_path = pt.absolute()
                command_full_path = command_full_path.resolve()
                if command_full_path.exists():
                    command_paths.append(command_full_path)
                    logging.debug(
                        "Configured custom module path at: %s", command_full_path
                    )

        for command_path in command_paths:
            for file in command_path.rglob("*.py"):
                try:
                    module_name = None
                    if str(file.absolute()).startswith(
                        str(self.BASE_DIR)
                    ):  # is a subdirectory of this module
                        module_name = (
                            str(file.absolute())
                            .removeprefix(str(self.BASE_DIR))
                            .removesuffix(".py")
                            .removeprefix("/")
                            .removesuffix("/__init__")
                            .replace(os.sep, ".")
                        )
                    else:
                        module_name = (
                            command_path.name
                            + "."
                            + str(file.absolute())
                            .removeprefix(str(command_path.absolute()))
                            .removesuffix(".py")
                            .removeprefix("/")
                            .removesuffix("/__init__")
                            .replace(os.sep, ".")
                        )
                    module = load_module_from_path(file, module_name)
                    if not module:
                        continue
                    for name, element in vars(module).items():
                        if name.startswith("_"):
                            continue
                        elif isinstance(element, tcve_command):
                            element.on("ready") # do it here so to avoid 
                            commands[element.name] = {
                                "name": element.name,
                                "command": element,
                            }
                        # tcve_exploits are also found by this function and registered automatically
                except Exception as ex:
                    logging.warning(
                        "Skipping module %s as we found an unrecoverable error with message: %s",
                        file,
                        str(ex),
                    )
                    self.stderr.print_exception()

        logging.info("%s commands loaded successfully", len(commands))
        aliases: dict[str, TCVECommand] = {}
        for command in commands:
            cmd = commands[command]["command"]
            cmd.on("completed")
            tcve_aliases = cmd.aliases
            if tcve_aliases and not cmd.hidden:
                aliases.update(**tcve_aliases)
        return dict(
            filter(
                lambda command: not command[1].get("command").hidden,
                commands.items(),  # pyright: ignore[reportUnknownMemberType]
            )
        ), aliases

    def __enter__(
        self,
    ) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_val: BaseException | None = None,
        exc_tb: TracebackType | None = None,
    ):
        for file in self.tmp_dir.glob("*"):
            if file.is_file():
                file.unlink()
            elif file.is_dir():
                file.rmdir()
        if self.proxy_client and self.proxy_client.is_persistent:
            logging.debug("Calling __exit__ from Context class")
            self.proxy_client.close(exc_type, exc_val, exc_tb)
            self.proxy_client = None
