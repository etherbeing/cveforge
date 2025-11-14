from utils.args import ForgeParser


class BruteForceParser(ForgeParser):
    def setUp(self) -> None:
        self.add_argument(
            "--query-param",
            "-Q",
            action="append",
            required=False,
            help="Marks the fields inside the url to crack",
        )
        self.add_argument(
            "--body-json",
            "-J",
            action="append",
            required=False,
            help="Marks the fields inside a json to crack",
        )
        self.add_argument(
            "--body-form",
            "-F",
            action="append",
            required=False,
            help="Marks the fields inside an application/multipart-form like body to crack",
        )
        self.add_argument(
            "--expects",
            "-E",
            required=False,
            help="Script like string that allows the user to do advance logic on bruteforcing",
        )
        self.add_argument(
            "--wordlist", "-W", required=True, help="Wordlist to use for bruteforcing"
        )
