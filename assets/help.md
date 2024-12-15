# CVE Forge Interactive CLI Documentation

Welcome to **CVE Forge**, a powerful tool designed for cybersecurity professionals to automate scanning, exploiting, and managing CVE vulnerabilities. This document provides detailed instructions for all the available commands and their usage within the interactive CLI environment.

---

## **Getting Started**

1. **Launch the CLI**:
   ```bash
   python cve_forge.py
   ```
2. Use `help` at any time to view available commands:
   ```bash
   help
   ```
3. **Exit** the program:
   ```bash
   exit
   ```

---

## **Commands Overview**

### **Target Management**

#### Add a Target
Add a new target for scanning and exploitation.
```bash
add_target <IP/Hostname>
```
Example:
```bash
add_target 192.168.1.10
```

#### List Targets
View all added targets.
```bash
list_targets
```

#### Remove a Target
Remove a specific target.
```bash
remove_target <Target_ID>
```
Example:
```bash
remove_target 1
```

---

### **Scanning and Exploitation**

#### Scan Targets for CVEs
Scan all or specific targets for known CVE vulnerabilities.
```bash
scan <Target_ID>
```
Example:
```bash
scan 1
```

#### Exploit Vulnerabilities
Automatically exploit discovered vulnerabilities.
```bash
exploit <Target_ID>
```
Example:
```bash
exploit 1
```

#### View Discovered Vulnerabilities
List all CVEs found during the scan.
```bash
view_cves <Target_ID>
```

---

### **Post-Exploitation Tools**

#### Upload Files
Upload a file to the target system.
```bash
upload <Target_ID> <Local_File_Path> <Remote_Path>
```
Example:
```bash
upload 1 /path/to/file /tmp/file
```

#### Privilege Escalation
Run predefined privilege escalation scripts.
```bash
privesc <Target_ID>
```
Example:
```bash
privesc 1
```

#### Open Interactive Shell
Access an exploited target’s shell.
```bash
shell <Target_ID>
```

#### Enumeration Tools
Perform enumeration to gather information about the target.
```bash
enumerate <Target_ID>
```
Supported Enumeration Types:
- `users`: List all system users.
- `services`: Enumerate running services.
- `files`: Search for sensitive files.

Example:
```bash
enumerate 1 users
```

---

### **Reporting and Visualization**

#### View Target Status Graph
Display a visual graph of target statuses (online/offline).
```bash
status_graph
```

#### Export Report
Export a detailed report of vulnerabilities and exploits.
```bash
export_report <Format>
```
Supported Formats:
- `txt`
- `json`
- `csv`

Example:
```bash
export_report json
```

---

### **Database Management**

#### View Database
List all stored targets, scans, and exploits.
```bash
view_db
```

#### Clear Database
Clear all stored data.
```bash
clear_db
```

---

### **Utilities for Pentesters**

#### Port Scanning
Perform a comprehensive port scan on a target.
```bash
port_scan <Target_ID>
```

#### Service Detection
Identify running services on open ports.
```bash
service_detect <Target_ID>
```

#### Network Mapping
Map the network around the target.
```bash
network_map <Target_ID>
```

#### Upload Custom Exploits
Add a custom exploit script to the tool.
```bash
upload_exploit <Exploit_File>
```

---

## **Examples**

1. Add a target, scan for CVEs, and exploit:
```bash
add_target 192.168.1.100
scan 1
view_cves 1
exploit 1
shell 1
```

2. Enumerate users and upload a file:
```bash
enumerate 1 users
upload 1 ./payload.exe C:\\Temp\\payload.exe
```

3. Export a report and visualize statuses:
```bash
export_report csv
status_graph
```

---

## **Community and Support**

If you encounter issues or have suggestions, please report them on our [GitHub repository](https://github.com/your-repo).

---

**Happy Pentesting! Stay Ethical!**
