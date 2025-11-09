"""
Handle global context for the current user, target host, port, arguments passed to the cli etc...
"""

import argparse
import getpass
import logging
from multiprocessing import Process
import os
import platform
import sys
import threading
from functools import lru_cache
from importlib import import_module
from logging import basicConfig
from pathlib import Path
from types import TracebackType
from typing import Any, Optional, Self, TypedDict

from core.commands.command_types import TCVECommand

try:
    from multiprocessing.connection import Connection
except ImportError:
    from multiprocessing.connection import PipeConnection as Connection # type: ignore

from tomllib import load

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory

from core.io import OUT
from utils.args import ForgeParser


class Args(ForgeParser):
    """Global context argument parser, responsible for handling this software as a normal command line software"""

    exit_cleanly = True
    "Handle program arguments"

    def setUp(self, *args: Any, **kwargs: Any) -> None:
        rce_arg_group = self.add_argument_group("Remote Code Execution")
        rce_arg_group.add_argument(
            "--enable-rce",
            "-eR",
            help="Enable Remote Code Execution, so there is a TCP server listening for incoming commands",
            action="store_true",
            default=False,
        )
        rce_arg_group.add_argument(
            "--security-signature",
            "-sS",
            help="""\
Security only once use code to identify the evoker for this process, once the evoker connect to the server\
there is a gap between the signature is expired by the process and the server running, to avoid this we must:
1. Allow only communications from the parent pid, using netstat we can see if the source port belongs to the\
given PID, if so then you can do the next steps.
2. To disallow blind rce vulnerabilities we must after the first step is done and communication begins,\
do a three steps handshake and test the SOURCE controls the keys for handling the signature he provided. A signature\
is the result of hashing a randomly created DSA key with sha512 hash algorithm. The keys aren't saved to disk\
instead they are managed in memory so unless the attacker can access this process memory pages then our communication\
is safe. The process is as follows:

        1. Client generate DSA key pairs.
        2. Client invoke the server process by passing a public key through the command line process args.
            2.1 (Optional) In case the server for RCE is remote use ECDH to exchange the keys between client and server
        3.   
""",
        )
        rce_arg_group.add_argument(
            "--public-key",
            "-pK",
            help="The client public key used for encrypted communication and avoid RCE or privilege escalation issues in CVE Forge",
        )
        self.add_argument(
            "command",
            help=(
                """
(Optional) CVE Forge command to run, e.g: \"ip\"; The example before does returns the \
public ip of the user and exit after that, this suppress the interactive behavior of \
the CVE Forge software and is mostly useful for when running quick commands.
"""
            ),
            nargs="?"
        )
        self.add_argument(
            "command_args",
            nargs=argparse.REMAINDER,
        )
        self.add_argument(
            "--debug",
            "-d",
            action="store_true",
            default=False
        )
        self.add_argument(
            "--log-level",
            "-l",
            default=logging.WARNING,
            type=int,
            choices=[
                logging.DEBUG,
                logging.INFO,
                logging.WARNING,
                logging.ERROR
            ]
        )
        self.add_argument(
            "--log-stdout",
            "-ls",
            action="store_true",
            help="Log content to standard output",
            default=False,
        )
        self.add_argument(
            "--http-timeout",
            help="Set the general HTTP timeout for the Forge",
            default=30,
            type=int
        )
        self.add_argument(
            "--web-address",
            "-W",
            help="Expose the UI of the forge in an specific IP and TCP port",
            default="127.0.0.1:3780"
        )

class CommandContext(TypedDict):
    current_command: TCVECommand|None
    remote_path: str|None

class Context:
    """Store all the settings and anything that is needed to be used global"""
    _singleton_instance = None
    _lock: threading.Lock = threading.Lock()
    log_to_stdout: bool = False

    def __new__(cls):
        """Singleton constructor"""
        with cls._lock:
            if cls._singleton_instance is None:
                cls._singleton_instance = super().__new__(cls)
        return cls._singleton_instance

    def __init__(self):
        logging.debug(
            "Initializing singleton Context instance, only one in the logs of these message should exist"
        )
        cli_args = Args(prog=self.SOFTWARE_NAME.lower().replace(" ", "_"))
        cli_args.setUp()
        namespace = cli_args.parse_args(sys.argv[1:])
        self.LIVE = not namespace.debug # type: ignore
        self.LOG_LEVEL = namespace.log_level
        self.enable_sudo_rce = namespace.enable_rce
        self.log_to_stdout = namespace.log_stdout
        self.http_timeout = namespace.http_timeout
        self.web_address = namespace.web_address

        if namespace.command:
            self.argv_command: list[str] = namespace.command_args
            self.argv_command.insert(0, namespace.command)
        else:
            self.argv_command = []

        if self.enable_sudo_rce:
            logging.warning(
                "RCE is enabled, please be aware of filesystem or network security, before doing this"
            )
        else:
            logging.debug("RCE is disabled")

        self.proxy_client: Optional[Any] = None

        if platform.system() == "Windows":
            self.data_dir = Path(
                os.getenv("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local\\"))
            )
        elif platform.system() == "Darwin":  # macOS
            self.data_dir = Path(os.path.expanduser("~/Library/Application Support/"))
        else:  # Linux and other UNIX-like OS
            self.data_dir = Path(os.path.expanduser("~/.local/share/"))
        self.data_dir = (self.data_dir / self.SOFTWARE_NAME).absolute()
        self.tmp_dir = self.data_dir / 'tmp'
        self.tmp_dir.mkdir(exist_ok=True)
        self.db_path = self.data_dir / self.DB_NAME.replace(" ", "_")
        self.db_path = self.db_path.absolute()
        base_dir = self.db_path.parent
        base_dir.mkdir(parents=True, exist_ok=True) 
        self.db_path.touch(exist_ok=True)
        assert self.db_path.exists()
        self.db_uri = f"sqlite:///{self.db_path}"
        self.history_path = self.data_dir / ".history.cve"
        self.custom_history_path = self.data_dir / ".histories/"
        logging.info("History file is at: %s", self.history_path)
        self.custom_history_path.mkdir(exist_ok=True, parents=True)
        logging.info("Program data folder is: %s", self.data_dir)

    @classmethod
    def require(cls, *args: str, **kwargs: Any):
        """
        Use args for required arguments and kwargs for optional arguments with default values
        for example:
        ```py
        Context.require(
            'username',
            'password',
            domain="something"
        )
        ```
        Please note that if a kwargs default is equal to None then that will make it also to be
        required with no default argument
        """
        instance = cls()
        for arg in [*args, *kwargs]:
            is_password = arg == "password"
            session: PromptSession[str] = PromptSession(
                history=(
                    FileHistory(str(instance.custom_history_path / arg))
                    if not is_password
                    else None
                ),
                auto_suggest=AutoSuggestFromHistory() if not is_password else None,
            )
            defaults = kwargs.get(arg, None)
            value: Any = getattr(instance, arg, defaults)
            while value is None:
                value = session.prompt(
                    f"{arg}{f'({defaults})' if defaults else ''}: ",
                    is_password=is_password,
                    complete_in_thread=True,
                )
            setattr(instance, arg, value)
        return True  # it returns whether or not all field are set, as the only way to leaving them in blank would be
        # sending CTRL + C ot break the loop we dont need to return False in any place

    def configure_logging(self):
        """
        Configure python default logger or root logger to store logs in a predetermined place
        """
        log_file = str(self.LOG_FILE).format(host_id=getpass.getuser())
        OUT.print(f"[yellow]Storing logs at: {log_file}[/yellow]")
        Path(log_file).touch(mode=755)
        basicConfig(
            level=(self.LOG_LEVEL),
            filename=None if self.log_to_stdout else log_file,
            filemode="a",  # Use 'a' for appending logs, or 'w' to overwrite
            format=self.LOG_FORMAT,
            datefmt=self.LOG_DATE_FTM,  # Optional: Customize timestamp format
            force=True,
        )
        logging.debug("Logging setup correctly")


    LIVE: bool = (
        False  # Live means actual production environment while, not live is when developing the forge
    )
    SOFTWARE_NAME = "CVE Forge"
    BASE_DIR = Path(__file__).parent.parent
    WEB_DIR = BASE_DIR / "web"
    COMMANDS_DIR = BASE_DIR/'core/commands'
    PAYLOAD_DIR = BASE_DIR / 'payloads'
    LOG_FILE: Path = BASE_DIR / ".cve.{host_id}.log"
    ASSETS_DIR = BASE_DIR / "assets"
    ASSETS_BASE_URL = "assets"
    TEXT_ART_DIR = ASSETS_DIR / "text_art"
    DB_NAME = "data/db.sqlite"
    CVE_FOLDER = ASSETS_DIR / "cvelistv5/cves"
    DEFAULT_CVE_CONFIG_PATH = BASE_DIR / ".cveforge.toml"
    # Exception Codes, useful for tree level deep communication
    EC_RELOAD = 3000
    EC_EXIT = 3001
    # Return codes, useful for arbitrary exits from the program
    RT_OK = 0
    RT_INVALID_COMMAND = 4000
    RT_ADDRESS_IN_USE = 4001

    SYSTEM_COMMAND_TOKEN = "@"
    MEDIA_FOLDER = ASSETS_DIR / "data/media"
    CVE_IGNORE_PATH = BASE_DIR / ".cveignore"
    SOFTWARE_SCHEMA_PATH = BASE_DIR / ".cveschema.json"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(funcName)s - %(message)s"
    LOG_DATE_FTM = "%Y-%m-%d %H:%M:%S"

    # Dynamic data needs class instantiation
    data_dir = None
    web_address = "127.0.0.1:3780"
    DB_ENGINE = "sqlite"
    DB_URI: str
    db_path: Path
    history_path: Path
    custom_history_path: Path
    sudo_pipe: Optional[Connection] = None
    running_childs: dict[str, Process] = {}

    protocol_name: Optional[str] = None

    _console_session: PromptSession[str]

    _command_context: CommandContext = {
        "current_command": None,
        "remote_path": None
    }

    @property
    def console_session(self):
        return self._console_session

    def set_console_session(self, value: PromptSession[str]):
        self._console_session =  value

    @property
    def command_context(
        self,
    ):
        """Returns a command related context"""
        return self._command_context

    def refresh_command_remote_path(self):
        self._command_context["remote_path"] = f"{self.protocol_name}://{self.username}{':*****' if self.password else ''}@{self.address}{f':{self.port}' if self.port else ''}//{self.share_name}{(f'/{self.context_path.removesuffix('/')}') if self.context_path else ''}"

    # cli: PromptSession[str] # Command Line
    # For shared context that needs to be transmitted through multiple commands,
    # (e.g. between network usage)
    username: Optional[str] = None
    password: Optional[str] = None
    address: Optional[str] = None
    port: Optional[int] = None
    domain: Optional[str] = None  # For protocols like smb or netbios
    share_name: Optional[str] = None  # For protocols like smb or netbios
    context_path: Optional[str] = None
    enable_sudo_rce: bool = (
        False  # WARNING this enable TCP server to run remote code execution feature
    )

    # trunk-ignore(ruff/B019)
    @lru_cache()
    def get_commands(self,):
        from core.commands.run import tcve_command
        commands: dict[str, TCVECommand] = {}
        logging.info("Loading commands...%s", " (commands are live reloaded)" if not self.LIVE else '')
        assert self.DEFAULT_CVE_CONFIG_PATH.exists()
        command_paths: list[Path] = [self.COMMANDS_DIR]
        with self.DEFAULT_CVE_CONFIG_PATH.open("rb") as config:
            config_data = load(config)
            toml_commands: list[str] = config_data.get("core", {}).get("commands", [])
            for command_path in toml_commands:
                if Path(command_path).is_absolute():
                    raise ValueError("Please make sure the path provided isn't an absolute Path")
                command_full_path = (self.BASE_DIR/command_path).absolute() # normalize it
                if command_full_path.exists():
                    command_paths.append(command_full_path)
                    logging.debug("Configured custom module path at: %s", command_full_path)
        
        for command_path in command_paths:
            for file in command_path.rglob("*.py"):
                module_src = str(file.relative_to(self.BASE_DIR)).replace(os.sep, ".")
                module_src = module_src.removesuffix('.py')
                try:
                    module = import_module(module_src)
                    for element in vars(module).values():
                        if isinstance(element, tcve_command):
                            commands[element.name] = {
                                "name": element.name,
                                "command": element
                            }
                        # tcve_exploits are also found by this function and registered automatically
                except Exception as ex:
                    logging.warning("Skipping module %s as we found an unrecoverable error with message: %s", module_src, str(ex))
        logging.info("%s commands loaded successfully", len(commands))
        aliases: dict[str, TCVECommand] = {}
        for command in commands:
            commands[command]["command"].on_commands_ready()
            if commands[command]["command"].has_aliases():
                aliases.update(**commands[command]["command"].expand_aliases())
        return commands, aliases

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
