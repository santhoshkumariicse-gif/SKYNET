# SKYNET RUNBOOK: Monitoring Agent Lifecycle & Restart Procedures
**Document ID:** RUNBOOK-AGT-001  
**Category:** Operations & Infrastructure  
**Tags:** agent, windows, linux, restart, troubleshooting, runbook  
**Last Updated:** 2026-09-25  

## Overview
The SKYNET monitoring agent runs as a native background service on Windows PCs, Linux servers, and edge Android devices. It continuously collects hardware telemetry (CPU, RAM, GPU, Disk, Network I/O) and sends authenticated heartbeats over TLS/WebSocket to the SKYNET backend.

## How to Restart the Windows Agent
To restart the monitoring agent on a Windows PC or server:

### Option 1: Elevated PowerShell or Command Prompt (Recommended)
1. Open PowerShell or Command Prompt as Administrator.
2. Execute the service control commands:
   ```cmd
   net stop SkynetAgent
   net start SkynetAgent
   ```
3. Alternatively, using PowerShell Service cmdlets:
   ```powershell
   Restart-Service -Name "SkynetAgent" -Force
   Get-Service -Name "SkynetAgent"
   ```

### Option 2: Windows Service Manager (services.msc)
1. Press `Win + R`, type `services.msc`, and press Enter.
2. Locate the service named **"SKYNET Endpoint Telemetry Service"** (`SkynetAgent`).
3. Right-click the service and select **Restart**.
4. Confirm status changes to **Running**.

### Option 3: Standalone Process Restart
If running in user-mode developer preview:
```powershell
taskkill /F /IM skynet_agent.exe
Start-Process -FilePath "C:\Program Files\Skynet\skynet_agent.exe" -ArgumentList "--daemon"
```

## How to Restart the Linux / Server Agent
On Linux servers running systemd:
```bash
sudo systemctl restart skynet-agent.service
sudo systemctl status skynet-agent.service
```

To review active telemetry transmission logs:
```bash
journalctl -u skynet-agent.service -n 50 -f
```

## Agent Health Verification & Connectivity Checks
After restarting, verify connectivity to the backend:
1. Ensure the device can reach the ingest gateway:
   ```powershell
   Test-NetConnection -ComputerName localhost -Port 8000
   ```
2. Verify heartbeat status in the web console under **Device Fleet** (`/devices`). The device should report a green **ONLINE** status with `last_seen < 30s`.
3. Agent configuration file is located at `C:\ProgramData\Skynet\agent_config.yaml`. Verify `backend_url` is set to `http://localhost:8000` (or production HTTPS gateway) and `agent_id` is populated.
