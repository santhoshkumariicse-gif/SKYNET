"""
SKYNET v5.0 — Wazuh XDR Integration Test Suite
Validates Wazuh cluster health checks, agent synchronization,
webhook alert ingestion, MITRE ATT&CK extraction, and SOAR active responses.
"""
import sys
import os
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.db.session import init_db

@pytest_asyncio.fixture(scope="module")
async def client():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_wazuh_status(client: AsyncClient):
    """Verifies Wazuh cluster status and manager daemon health reporting."""
    res = await client.get("/api/v1/wazuh/status")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "manager_version" in data
    assert "agent_summary" in data

@pytest.mark.asyncio
async def test_wazuh_agents_list(client: AsyncClient):
    """Verifies retrieval of Wazuh monitored endpoints across the fleet."""
    res = await client.get("/api/v1/wazuh/agents")
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert "agents" in data
    assert len(data["agents"]) > 0
    # Check agent fields
    agent = data["agents"][0]
    assert "id" in agent
    assert "name" in agent
    assert "status" in agent

@pytest.mark.asyncio
async def test_wazuh_vulnerabilities(client: AsyncClient):
    """Verifies Wazuh Vulnerability Detector inventory and CVSS scoring."""
    res = await client.get("/api/v1/wazuh/vulnerabilities")
    assert res.status_code == 200
    data = res.json()
    assert "vulnerabilities" in data
    assert len(data["vulnerabilities"]) > 0
    vuln = data["vulnerabilities"][0]
    assert "cve" in vuln
    assert "severity" in vuln
    assert "cvss3_score" in vuln

@pytest.mark.asyncio
async def test_wazuh_alert_webhook_ingestion(client: AsyncClient):
    """Verifies live webhook ingestion, normalization, and alert generation."""
    payload = {
        "timestamp": "2026-09-26T00:30:00.000Z",
        "rule": {
            "id": "90015",
            "level": 14,
            "description": "Wazuh Alert: Ransomware Shadow Copy Deletion (vssadmin.exe)",
            "mitre": {
                "id": ["T1490"],
                "tactic": ["Impact"],
                "technique": ["Inhibit System Recovery"]
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
                    "image": "C:\\Windows\\System32\\vssadmin.exe",
                    "commandLine": "vssadmin.exe delete shadows /all /quiet",
                    "sourceIp": "192.168.1.100"
                }
            }
        },
        "full_log": "Wazuh agent detected vssadmin deleting volume shadow copies."
    }

    res = await client.post("/api/v1/wazuh/webhook", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "INGESTED"
    assert data["severity"] == "CRITICAL"
    assert data["mitre_technique"] == "T1490"
    assert "alert_id" in data
    assert "audit_hmac" in data

@pytest.mark.asyncio
async def test_wazuh_active_response_rbac(client: AsyncClient):
    """Verifies role-based access control and HMAC audit on active response execution."""
    req = {
        "agent_id": "001",
        "command": "firewall-drop",
        "arguments": ["-ip", "10.0.0.99"]
    }

    # 1. READ_ONLY role attempting containment must be rejected with 403 Forbidden
    ro_login = await client.post("/api/v1/auth/login", json={"username": "readonly", "password": "ReadOnlySecure2026!"})
    assert ro_login.status_code == 200
    ro_token = ro_login.json()["access_token"]
    ro_headers = {"Authorization": f"Bearer {ro_token}"}

    ro_res = await client.post("/api/v1/wazuh/active-response", json=req, headers=ro_headers)
    assert ro_res.status_code == 403
    assert "Access denied" in ro_res.json()["detail"]

    # 2. Authenticated Admin request must succeed with HMAC audit signature
    login_res = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    auth_res = await client.post("/api/v1/wazuh/active-response", json=req, headers=headers)
    assert auth_res.status_code == 200
    data = auth_res.json()
    assert data["agent_id"] == "001"
    assert data["command"] == "firewall-drop"
    assert "hmac_signature" in data
