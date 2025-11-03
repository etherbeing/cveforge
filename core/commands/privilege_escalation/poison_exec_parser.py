from utils.args import ForgeParser


class PoisonExecParser(ForgeParser):
    def setUp(self) -> None:
        self.add_argument("--hostname")
        self.add_argument("--port")
        self.add_argument("--identity-file")
        self.add_argument("--username")
        self.add_argument("--passphrase")
        self.add_argument("--vulnerable-path")
        self.add_argument("--backdoor-user")
        self.add_argument("--backdoor-password", required=False)
