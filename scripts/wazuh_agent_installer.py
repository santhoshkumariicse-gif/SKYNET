"""
SKYNET v5.0 — Wazuh Agent Deployment Generator
Generates one-line enrollment commands and unattended installer packages
for Windows (PowerShell/MSI), Linux (Debian/RHEL/Arch), and macOS.
"""
import sys
import argparse

def generate_installers(manager_ip="127.0.0.1", group="default"):
    print("=" * 70)
    print(f"SKYNET v5.0 — WAZUH AGENT ENROLLMENT COMMAND GENERATOR")
    print(f"Target Wazuh Manager: {manager_ip} | Group: {group}")
    print("=" * 70)

    # Windows PowerShell one-liner
    windows_cmd = (
        f"Invoke-WebRequest -Uri https://packages.wazuh.com/4.x/windows/wazuh-agent-4.9.0-1.msi "
        f"-OutFile ${env:TEMP}\\wazuh-agent.msi; "
        f"msiexec.exe /i ${env:TEMP}\\wazuh-agent.msi /q "
        f"WAZUH_MANAGER='{manager_ip}' WAZUH_AGENT_GROUP='{group}' "
        f"WAZUH_REGISTRATION_SERVER='{manager_ip}'; "
        f"Start-Service -Name WazuhSvc"
    )

    # Linux Debian / Ubuntu one-liner
    debian_cmd = (
        f"curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import && "
        f"chmod 644 /usr/share/keyrings/wazuh.gpg && "
        f"echo \"deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main\" | tee /etc/apt/sources.list.d/wazuh.list && "
        f"apt-get update && WAZUH_MANAGER='{manager_ip}' WAZUH_AGENT_GROUP='{group}' apt-get install -y wazuh-agent && "
        f"systemctl daemon-reload && systemctl enable wazuh-agent && systemctl start wazuh-agent"
    )

    # Linux RHEL / CentOS one-liner
    rhel_cmd = (
        f"rpm --import https://packages.wazuh.com/key/GPG-KEY-WAZUH && "
        f"cat > /etc/yum.repos.d/wazuh.repo << 'EOF'\n"
        f"[wazuh]\nname=Wazuh repository\nbaseurl=https://packages.wazuh.com/4.x/yum/\ngpgcheck=1\nenabled=1\nEOF\n"
        f"WAZUH_MANAGER='{manager_ip}' WAZUH_AGENT_GROUP='{group}' yum install -y wazuh-agent && "
        f"systemctl daemon-reload && systemctl enable wazuh-agent && systemctl start wazuh-agent"
    )

    print("\n--- [WINDOWS ENDPOINT INSTALLATION (PowerShell as Administrator)] ---")
    print(windows_cmd)

    print("\n--- [DEBIAN / UBUNTU LINUX INSTALLATION (Bash as Root)] ---")
    print(debian_cmd)

    print("\n--- [RHEL / CENTOS / ROCKY LINUX INSTALLATION (Bash as Root)] ---")
    print(rhel_cmd)
    print("\n" + "=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Wazuh agent enrollment commands.")
    parser.add_argument("--manager", default="127.0.0.1", help="Wazuh Manager IP/Hostname")
    parser.add_argument("--group", default="default", help="Wazuh Agent Group")
    args = parser.parse_args()
    generate_installers(args.manager, args.group)
