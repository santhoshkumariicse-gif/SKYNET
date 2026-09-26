# SKYNET Windows Monitoring Agent

Lightweight, high-performance endpoint infrastructure monitoring agent designed for Windows Workstations, Laptops, and Servers.

---

## 1. Features

- **Hardware Telemetry Gathering:**
  - **CPU Utilization:** Aggregate and multi-core CPU load percentages via `psutil`.
  - **Memory (RAM) Usage:** Percentage, active MB, and total available memory.
  - **Disk Utilization:** Primary system drive utilization and storage bounds.
  - **GPU Utilization:** Dedicated NVIDIA GPU core metrics via `GPUtil` with automatic graceful fallback to `0.0%` if unequipped.
  - **Network I/O:** Delta calculation for RX/TX megabytes per interval.
  - **Battery & Power:** Real-time percentage tracking for laptops and mobile endpoints.
- **Autonomous Registration:**
  - Performs initial registration with SKYNET Gateway (`POST /devices/register`) on startup.
- **Resilient Dispatch:**
  - Periodic 30-second telemetry polling.
  - Exponential backoff with jitter on network disconnects.
  - Signal-aware graceful shutdown (`SIGINT`, `SIGTERM`).
  - API Key authentication via `X-Agent-Key` header.

---

## 2. Directory Structure

```text
windows-agent/
├── agent.py            # Main agent daemon lifecycle and dispatch loop
├── collector.py        # Hardware and system metrics gathering module
├── config.py           # Configuration parameters and environment bindings
├── requirements.txt    # Python dependencies (psutil, GPUtil, requests)
└── README.md           # Installation and usage instructions
```

---

## 3. Installation & Setup

### Prerequisites
- Python 3.9+ installed on Windows.
- Administrator privileges (recommended for low-level system metrics).

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 2: Environment Configuration
You can configure the agent via environment variables or rely on secure defaults:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `SKYNET_BACKEND_URL` | `http://localhost:8000/api/v1` | URL of the central FastAPI backend gateway |
| `SKYNET_AGENT_KEY` | `skynet_agent_default_secret_token_2026` | Shared agent authentication key |
| `SKYNET_DEVICE_ID` | Auto-generated UUID5 | Unique hardware identifier |
| `SKYNET_COLLECTION_INTERVAL` | `30` | Cadence in seconds between metric dispatches |

### Step 3: Run the Agent
```powershell
python agent.py
```

### Running as a Windows Background Service (NSSM)
To keep the agent running persistently as a Windows service:
```powershell
# Download NSSM (Non-Sucking Service Manager)
nssm install SKYNETAgent "C:\Python311\python.exe" "C:\skynet\windows-agent\agent.py"
nssm set SKYNETAgent AppDirectory "C:\skynet\windows-agent"
nssm set SKYNETAgent Start SERVICE_AUTO_START
nssm start SKYNETAgent
```
