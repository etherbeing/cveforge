import argparse
from utils.args import ForgeParser


class CVE20256018Parser(ForgeParser):
    def setUp(self) -> None:
        self.description = "CVE-2025-6018/6019 PAM Environment Injection Exploit"
        self.formatter_class = argparse.RawDescriptionHelpFormatter
        self.epilog = """
            Examples:
                python3 %(prog)s -i 192.168.1.100 -u testuser -p password123
                python3 %(prog)s -i target.com -u admin -k ~/.ssh/id_rsa
        """
        self.add_argument("-i", "--hostname", required=True, help="Target hostname or IP")
        self.add_argument("-u", "--username", required=True, help="SSH username")
        self.add_argument("-p", "--password", help="SSH password")
        self.add_argument("-k", "--key", dest="key_filename", help="SSH private key file")
        self.add_argument("-kP", "--key-passphrase", dest="key_passphrase", help="SSH private key passphrase")
        self.add_argument("--port", type=int, default=22, help="SSH port (default: 22)")
