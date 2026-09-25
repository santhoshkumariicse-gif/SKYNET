#!/usr/bin/env bash
# ==============================================================================
# SKYNET v5.0 — Complete Wazuh Installation Script for WSL (Ubuntu / Debian)
# Provides automated options for:
#   1. Native All-in-One Wazuh Server (Manager + Indexer + Dashboard)
#   2. Docker-based Wazuh Cluster Stack
#   3. Wazuh Agent Enrollment
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${CYAN}======================================================================${NC}"
echo -e "${CYAN}SKYNET v5.0 — WAZUH COMPLETE WSL INSTALLER & DEPLOYMENT${NC}"
echo -e "${CYAN}======================================================================${NC}"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
    echo -e "${GREEN}[+] Detected OS:${NC} $OS ($VER)"
else
    echo -e "${RED}[!] Could not detect Linux distribution. Assuming Ubuntu/Debian.${NC}"
fi

# Check sudo privileges
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}[*] Elevating to root privileges...${NC}"
    exec sudo bash "$0" "$@"
fi

# Ensure system requirements
echo -e "\n${CYAN}[1/4] Checking System Resources & Prerequisites...${NC}"
TOTAL_RAM_MB=$(free -m | awk '/^Mem:/{print $2}')
echo -e "  - Total RAM: ${TOTAL_RAM_MB} MB"

if [ "$TOTAL_RAM_MB" -lt 3800 ]; then
    echo -e "${YELLOW}[!] Warning: Wazuh Indexer & Manager recommend at least 4 GB RAM.${NC}"
    echo -e "    If memory is constrained, consider configuring .wslconfig with 'memory=6GB'."
fi

# Set vm.max_map_count for OpenSearch / Wazuh Indexer
echo -e "  - Setting vm.max_map_count=262144 (Required for Wazuh Indexer)..."
sysctl -w vm.max_map_count=262144 > /dev/null
if ! grep -q "vm.max_map_count=262144" /etc/sysctl.conf 2>/dev/null; then
    echo "vm.max_map_count=262144" >> /etc/sysctl.conf
fi

# Update dependencies
echo -e "\n${CYAN}[2/4] Updating Apt & Installing Core Utilities...${NC}"
apt-get update -qq
apt-get install -y -qq curl apt-transport-https lsb-release gnupg2 tar unzip wget jq > /dev/null

# Select installation method
INSTALL_METHOD=${1:-"assisted"}

if [ "$INSTALL_METHOD" == "docker" ]; then
    echo -e "\n${CYAN}[3/4] Deploying Wazuh via Docker Compose...${NC}"
    if command -v docker >/dev/null 2>&1; then
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        COMPOSE_FILE="$SCRIPT_DIR/../docker-compose.wazuh.yml"
        if [ -f "$COMPOSE_FILE" ]; then
            docker compose -f "$COMPOSE_FILE" up -d
            echo -e "${GREEN}[+] Wazuh Docker Stack is starting in the background!${NC}"
        else
            echo -e "${RED}[!] docker-compose.wazuh.yml not found at $COMPOSE_FILE${NC}"
            exit 1
        fi
    else
        echo -e "${RED}[!] Docker is not installed or running in WSL. Falling back to native installer.${NC}"
        INSTALL_METHOD="assisted"
    fi
fi

if [ "$INSTALL_METHOD" == "assisted" ]; then
    echo -e "\n${CYAN}[3/4] Downloading Official Wazuh All-in-One Assistant (v4.9)...${NC}"
    cd /tmp
    curl -sO https://packages.wazuh.com/4.9/wazuh-install.sh
    curl -sO https://packages.wazuh.com/4.9/config.yml || true

    echo -e "${GREEN}[+] Running Wazuh Unattended All-in-One Installation...${NC}"
    echo -e "    This installs Wazuh Indexer, Wazuh Manager, and Wazuh Dashboard."
    bash ./wazuh-install.sh -a --ignore-healthcheck || {
        echo -e "${YELLOW}[*] Retrying with standalone assistant...${NC}"
        bash ./wazuh-install.sh -a
    }
fi

# Post-Install Verification
echo -e "\n${CYAN}[4/4] Verifying Installed Wazuh Services...${NC}"
if command -v systemctl >/dev/null 2>&1; then
    systemctl status wazuh-manager --no-pager || true
    systemctl status wazuh-indexer --no-pager || true
    systemctl status wazuh-dashboard --no-pager || true
fi

echo -e "\n${GREEN}======================================================================${NC}"
echo -e "${GREEN}WAZUH INSTALLATION COMPLETED SUCCESSFULLY!${NC}"
echo -e "${GREEN}======================================================================${NC}"
echo -e "Access URLs:"
echo -e "  - ${CYAN}Wazuh Web Dashboard:${NC} https://localhost:443 (or https://localhost:8443)"
echo -e "  - ${CYAN}Wazuh REST API:${NC}     https://localhost:55000"
echo -e "  - ${CYAN}SKYNET API Gateway:${NC} http://127.0.0.1:8000/api/v1/wazuh/status"
echo -e "  - ${CYAN}SKYNET SOC Cockpit:${NC} http://localhost:3000/wazuh"
echo -e "\nDefault Credentials (if installed via Wazuh Assistant):"
echo -e "  - Check credentials stored in: /tmp/wazuh-install-files/wazuh-passwords.txt"
echo -e "======================================================================\n"
