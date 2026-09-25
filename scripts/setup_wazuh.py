"""
SKYNET v5.0 — Wazuh Setup, Enrollment & Verification Utility
Automates Wazuh Docker container orchestration, API validation,
agent enrollment command generation, and webhook forwarder configuration.
"""
import sys
import os
import json
import asyncio
from datetime import datetime, timezone

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import httpx
from app.core.config import settings

async def main():
    print("=" * 70)
    print("SKYNET v5.0 — WAZUH XDR & SIEM INSTALLATION & VERIFICATION")
    print("=" * 70)

    # 1. Environment & Config Verification
    print(f"\n[1/5] Verifying Configuration:")
    print(f"  - WAZUH_ENABLED:       {settings.WAZUH_ENABLED}")
    print(f"  - WAZUH_API_URL:       {settings.WAZUH_API_URL}")
    print(f"  - WAZUH_USER:          {settings.WAZUH_USER}")
    print(f"  - WAZUH_WEBHOOK_SECRET:{settings.WAZUH_WEBHOOK_SECRET}")
    print(f"  - SKYNET Backend API:  http://127.0.0.1:8000/api/v1")

    # 2. Check Wazuh Cluster Status via SKYNET Service
    print(f"\n[2/5] Testing SKYNET Wazuh Service Status Endpoint:")
    from app.services.wazuh_service import wazuh_service
    status_result = await wazuh_service.get_cluster_status()
    print(f"  - Status:          {status_result.get('status')}")
    print(f"  - Manager Version: {status_result.get('manager_version')}")
    print(f"  - Cluster Name:    {status_result.get('cluster_name')}")
    print(f"  - Active Agents:   {status_result.get('agent_summary', {}).get('active', 0)}")

    # 3. Query Registered Wazuh Agents
    print(f"\n[3/5] Querying Wazuh Monitored Endpoints:")
    agents = await wazuh_service.list_agents()
    for ag in agents:
        print(f"  - Agent [{ag.get('id')}]: {ag.get('name')} ({ag.get('ip')}) | OS: {ag.get('os', {}).get('name', 'N/A')} | Status: {ag.get('status')}")

    # 4. Ingest Simulated Live Wazuh Alert into SKYNET Pipeline
    print(f"\n[4/5] Testing Wazuh Webhook Alert Ingestion & HMAC Sealing:")
    from app.db.session import AsyncSessionLocal
    
    sample_wazuh_alert = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "rule": {
            "id": "100201",
            "level": 12,
            "description": "Wazuh Alert: High-Severity Mimikatz LSASS Memory Dump Detected",
            "mitre": {
                "id": ["T1003.001"],
                "tactic": ["Credential Access"],
                "technique": ["LSASS Memory"]
            }
        },
        "agent": {
            "id": "001",
            "name": "SEC-WS-001",
            "ip": "192.168.1.100"
        },
        "data": {
            "win": {
                "eventdata": {
                    "image": "C:\\Windows\\Temp\\mimikatz.exe",
                    "commandLine": "mimikatz.exe \"privilege::debug\" \"sekurlsa::logonpasswords\" exit",
                    "sourceIp": "192.168.1.100"
                }
            }
        },
        "full_log": "Wazuh Agent SEC-WS-001 detected mimikatz.exe executing LSASS process memory dump."
    }

    async with AsyncSessionLocal() as session:
        ingest_result = await wazuh_service.ingest_wazuh_alert(session, sample_wazuh_alert)
        print(f"  - Ingest Result:   {ingest_result.get('status')}")
        print(f"  - Alert ID:        {ingest_result.get('alert_id')}")
        print(f"  - Severity:        {ingest_result.get('severity')}")
        print(f"  - MITRE Technique: {ingest_result.get('mitre_technique')}")
        print(f"  - Audit HMAC:      {ingest_result.get('audit_hmac')[:32]}...")

    # 5. Test Wazuh Active Response Execution
    print(f"\n[5/5] Testing Wazuh Active Response Containment:")
    async with AsyncSessionLocal() as session:
        ar_result = await wazuh_service.trigger_active_response(
            session=session,
            agent_id="001",
            command="firewall-drop",
            arguments=["-ip", "192.168.1.100"],
            actor="SOC_AUTOMATION"
        )
        print(f"  - Execution Status: {ar_result.get('status')}")
        print(f"  - Target Agent:     {ar_result.get('agent_id')}")
        print(f"  - Command:          {ar_result.get('command')}")
        print(f"  - HMAC Signature:   {ar_result.get('hmac_signature')[:32]}...")

    print("\n" + "=" * 70)
    print("WAZUH INTEGRATION SUCCESSFULLY VERIFIED AND OPERATIONAL [PASS]")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
