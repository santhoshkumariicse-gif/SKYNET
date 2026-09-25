"""
SKYNET v5.0 — Autonomous SOC End-to-End Test Suite
Tests telemetry ingestion, detection engine, threat intel enrichment,
temporal correlation, multi-agent AI investigation, and SOAR active defense.
"""
import sys
import os
import time
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.db.session import init_db
from app.detection.sigma_engine import sigma_engine
from app.detection.ioc_matcher import ioc_matcher
from app.schemas.schemas import TelemetryEvent


@pytest_asyncio.fixture(scope="module")
async def client():
    """Initializes database schema and yields an asynchronous HTTP test client."""
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Verifies system health check endpoint."""
    res = await client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "operational"
    assert data["platform"] == "SKYNET v5.0"


@pytest.mark.asyncio
async def test_auth_login_and_profile(client: AsyncClient):
    """Verifies JWT issuance and profile retrieval."""
    login_res = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me_res = await client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    user = me_res.json()
    assert user["username"] == "admin"
    assert user["role"] == "ADMIN"


@pytest.mark.asyncio
async def test_sigma_detection_rules():
    """Tests the in-memory Sigma rule engine against known attacker techniques."""
    # Test 1: Encoded PowerShell (T1059.001)
    ev_ps = TelemetryEvent(
        host_name="TEST-HOST-01",
        process_name="powershell.exe",
        process_command_line="powershell.exe -NonI -W Hidden -Enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoA..."
    )
    matches_ps = sigma_engine.evaluate_event(ev_ps)
    assert len(matches_ps) >= 1
    assert matches_ps[0].rule_id == "SIGMA-WIN-001"
    assert matches_ps[0].mitre_technique == "T1059.001"
    assert matches_ps[0].severity == "HIGH"

    # Test 2: LSASS Memory Dump (T1003.001)
    ev_lsass = TelemetryEvent(
        host_name="TEST-HOST-01",
        process_name="procdump64.exe",
        process_command_line="procdump64.exe -ma lsass.exe C:\\temp\\lsass.dmp"
    )
    matches_lsass = sigma_engine.evaluate_event(ev_lsass)
    assert len(matches_lsass) >= 1
    assert matches_lsass[0].rule_id == "SIGMA-WIN-002"
    assert matches_lsass[0].severity == "CRITICAL"

    # Test 3: Shadow Copy Deletion (T1490)
    ev_vss = TelemetryEvent(
        host_name="TEST-HOST-01",
        process_name="vssadmin.exe",
        process_command_line="vssadmin.exe delete shadows /all /quiet"
    )
    matches_vss = sigma_engine.evaluate_event(ev_vss)
    assert len(matches_vss) >= 1
    assert matches_vss[0].rule_id == "SIGMA-WIN-004"
    assert matches_vss[0].severity == "CRITICAL"


@pytest.mark.asyncio
async def test_ioc_matching_logic():
    """Verifies IOC matching against seeded malicious and clean indicators."""
    from app.db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        # Malicious C2 IP
        ev_c2 = TelemetryEvent(
            host_name="TEST-HOST-01",
            dst_ip="185.220.101.5",
            dst_port=443
        )
        matches_c2 = await ioc_matcher.evaluate_event(session, ev_c2)
        assert len(matches_c2) >= 1
        assert matches_c2[0].rule_id == "IOC-IP-001"
        assert matches_c2[0].severity == "CRITICAL"

        # Clean IP
        ev_clean = TelemetryEvent(
            host_name="TEST-HOST-01",
            dst_ip="8.8.8.8",
            dst_port=53
        )
        matches_clean = await ioc_matcher.evaluate_event(session, ev_clean)
        assert len(matches_clean) == 0


@pytest.mark.asyncio
async def test_telemetry_batch_ingest_and_correlation(client: AsyncClient):
    """
    Ingests a multi-stage attack sequence via the telemetry ingestion API,
    verifies detection generation, automatic incident correlation, and AI investigation.
    """
    test_host = f"TEST-RIG-{int(time.time())}"
    batch = {
        "agent_key": "skynet_agent_default_secret_token_2026",
        "hostname": test_host,
        "ip_address": "192.168.10.45",
        "os_name": "Windows",
        "os_version": "11 Pro",
        "device_type": "Workstation",
        "cpu_usage": 45.0,
        "memory_usage": 72.0,
        "disk_usage": 50.0,
        "events": [
            {
                "event_id_code": 1,
                "event_source": "sysmon",
                "host_name": test_host,
                "process_id": 3412,
                "process_name": "powershell.exe",
                "process_command_line": "powershell.exe -NoP -Enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoA...",
                "user_name": "victim_user"
            },
            {
                "event_id_code": 3,
                "event_source": "sysmon",
                "host_name": test_host,
                "process_id": 3412,
                "process_name": "powershell.exe",
                "dst_ip": "185.220.101.5",
                "dst_port": 443,
                "user_name": "victim_user"
            },
            {
                "event_id_code": 1,
                "event_source": "sysmon",
                "host_name": test_host,
                "process_id": 5104,
                "process_name": "procdump64.exe",
                "process_command_line": "procdump64.exe -ma lsass.exe C:\\temp\\lsass.dmp",
                "user_name": "SYSTEM",
                "process_hash_sha256": "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f"
            }
        ]
    }

    res = await client.post("/api/v1/telemetry/ingest", json=batch)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["events_processed"] == 3
    assert data["alerts_generated"] >= 3
    assert data["incidents_affected"] >= 1

    # Verify Endpoint status is now COMPROMISED
    asset_res = await client.get(f"/api/v1/assets?search={test_host}")
    assert asset_res.status_code == 200
    assets = asset_res.json()
    assert len(assets) > 0
    assert assets[0]["status"] == "COMPROMISED"


@pytest.mark.asyncio
async def test_ai_investigation_dossier(client: AsyncClient):
    """Verifies autonomous AI SOC investigation on a correlated incident."""
    inc_res = await client.get("/api/v1/incidents")
    assert inc_res.status_code == 200
    incidents = inc_res.json()
    assert len(incidents) > 0

    target_inc = incidents[0]
    inv_res = await client.post(f"/api/v1/incidents/{target_inc['id']}/investigate")
    assert inv_res.status_code == 200
    dossier = inv_res.json()

    assert dossier["incident_number"] == target_inc["incident_number"]
    assert dossier["confidence_score"] >= 0.7
    assert dossier["recommended_severity"] in ["HIGH", "CRITICAL"]
    assert len(dossier["executive_summary"]) > 20
    assert len(dossier["technical_root_cause"]) > 20
    assert len(dossier["suggested_actions"]) >= 1


@pytest.mark.asyncio
async def test_soar_containment_and_audit(client: AsyncClient):
    """Verifies SOAR host isolation action with cryptographic HMAC token and audit log entry."""
    req_payload = {
        "action_type": "ISOLATE_HOST",
        "target_identifier": "TEST-RIG-007",
        "reason": "Autonomous Tier-1 triage identified Cobalt Strike C2 activity",
        "rollback_plan": "Restore network adapter via Asset Management"
    }

    soar_res = await client.post("/api/v1/soar/execute", json=req_payload)
    assert soar_res.status_code == 200
    action = soar_res.json()

    assert action["status"] == "EXECUTED"
    assert action["action_type"] == "ISOLATE_HOST"
    assert action["target"] == "TEST-RIG-007"
    assert len(action["signed_token"]) == 64 # HMAC-SHA256 hex string

    # Verify Host is now ISOLATED in Fleet
    asset_res = await client.get("/api/v1/assets?search=TEST-RIG-007")
    assert asset_res.status_code == 200
    assets = asset_res.json()
    assert len(assets) > 0
    assert assets[0]["status"] == "ISOLATED"

    # Verify Audit Trail recorded the containment action
    audit_res = await client.get("/api/v1/audit/logs?limit=5")
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert any(l["action"] == "SOAR_ISOLATE_HOST" and l["resource_id"] == "TEST-RIG-007" for l in logs)


@pytest.mark.asyncio
async def test_mitre_coverage_matrix(client: AsyncClient):
    """Verifies MITRE ATT&CK coverage calculation and live detection aggregation."""
    res = await client.get("/api/v1/mitre/coverage")
    assert res.status_code == 200
    cov = res.json()
    assert cov["total_techniques_tracked"] >= 15
    assert cov["overall_coverage_pct"] >= 70.0
    assert "Execution" in cov["tactics"]
    assert "Credential Access" in cov["tactics"]
    assert "Command and Control" in cov["tactics"]


@pytest.mark.asyncio
async def test_62_processes_verification(client: AsyncClient):
    """Verifies all 62 architectural processes (Documents 1 through 62)."""
    # 1. Fetch registry
    res = await client.get("/api/v1/processes")
    assert res.status_code == 200
    data = res.json()
    assert data["total_processes"] == 62
    assert data["compliance_score_pct"] == 100.0
    assert len(data["processes"]) == 62

    # 2. Run master audit
    verify_res = await client.post("/api/v1/processes/verify-all")
    assert verify_res.status_code == 200
    vdata = verify_res.json()
    assert vdata["total_processes_evaluated"] == 62
    assert vdata["processes_passed"] == 62
    assert vdata["status"] == "ALL_62_PROCESSES_OPERATIONAL"
    assert vdata["compliance_grade"] == "A+ ENTERPRISE AUTONOMOUS"


@pytest.mark.asyncio
async def test_threat_hunting_query_and_saved_repository(client: AsyncClient):
    """Verifies threat hunting query against event lake and query repository persistence."""
    # 1. Execute Hunt Query
    hunt_res = await client.post("/api/v1/hunt/query", json={
        "query": "process.name = 'powershell.exe' AND network.destination_ip IN threat_intel.malicious_ips",
        "time_range": "24h"
    })
    assert hunt_res.status_code == 200
    data = hunt_res.json()
    assert "results" in data
    assert len(data["results"]) >= 1
    assert data["hosts_affected"] >= 1
    assert data["execution_time_ms"] > 0

    # 2. Save Hunt Query
    save_res = await client.post("/api/v1/hunt/save", json={
        "name": "Integration Test Cobalt Sweep",
        "query": "process.name = 'powershell.exe'",
        "mitre_technique": "T1059.001"
    })
    assert save_res.status_code == 200
    assert save_res.json()["name"] == "Integration Test Cobalt Sweep"

    # 3. Retrieve Saved Hunts
    saved_res = await client.get("/api/v1/hunt/saved")
    assert saved_res.status_code == 200
    saved_list = saved_res.json()
    assert any(h["name"] == "Integration Test Cobalt Sweep" for h in saved_list)


@pytest.mark.asyncio
async def test_human_in_the_loop_approval_containment_and_hmac(client: AsyncClient):
    """Verifies human-in-the-loop approval gating, cryptographic HMAC-SHA256 signature, and isolation."""
    # 1. List Approvals
    apv_res = await client.get("/api/v1/approvals")
    data = apv_res.json()
    if len(data) == 0:
        await init_db()
        apv_res = await client.get("/api/v1/approvals")
        data = apv_res.json()
    assert len(data) >= 1
    target_apv = data[0]
    apv_id = target_apv["id"]

    # 2. Approve Action
    approve_res = await client.post(f"/api/v1/approvals/{apv_id}/approve")
    assert approve_res.status_code == 200
    app_data = approve_res.json()
    assert app_data["status"] == "APPROVED"
    token = app_data.get("signed_token") or app_data.get("hmac_signature")
    assert token is not None and len(token) == 64

    # 3. Verify in Audit Logs
    audit_res = await client.get("/api/v1/audit/logs?limit=10")
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert any("APPROVAL" in l["action"] and l["resource_id"] in [target_apv["target"], apv_id] for l in logs)


@pytest.mark.asyncio
async def test_threat_intel_blocklist_addition(client: AsyncClient):
    """Verifies adding indicators directly to the firewall perimeter drop blocklist and subsequent lookup."""
    test_ip = "198.51.100.77"
    # 1. Add to Blocklist
    block_res = await client.post("/api/v1/threatintel/blocklist", json={
        "ioc_value": test_ip,
        "ioc_type": "IP",
        "reason": "Integration Test Malicious C2 Node"
    })
    assert block_res.status_code == 200
    bdata = block_res.json()
    assert bdata["status"] == "BLOCKED"
    assert bdata["threat_score"] == 100

    # 2. Query Indicator to verify real DB persistence
    lookup_res = await client.post("/api/v1/threatintel/lookup", json={
        "ioc_type": "IP",
        "value": test_ip
    })
    assert lookup_res.status_code == 200
    ldata = lookup_res.json()
    assert ldata["threat_score"] == 100
    assert ldata["is_malicious"] is True
    assert ldata["verdict"] == "MALICIOUS"


@pytest.mark.asyncio
async def test_automation_workflows_and_execution(client: AsyncClient):
    """Verifies automated workflow discovery from repository and multi-stage pipeline execution."""
    # 1. Get Workflows
    wf_res = await client.get("/api/v1/automation/workflows")
    assert wf_res.status_code == 200
    wdata = wf_res.json()
    assert wdata["active_pipelines"] >= 3
    assert wdata["subsystem_health"]["core_detection"] == "HEALTHY"
    assert wdata["subsystem_health"]["soar_defense"] == "HEALTHY"

    # 2. Execute 12-Stage Pipeline
    exec_res = await client.post("/api/v1/automation/execute", json={
        "workflow_id": "WF-01",
        "target": "WS-182",
        "incident_id": "INC-2026-0004"
    })
    assert exec_res.status_code == 200
    edata = exec_res.json()
    assert edata["workflow_id"] == "WF-01"
    assert len(edata["stages"]) == 12
    assert edata["status"] == "WAITING_APPROVAL"
    assert edata["latency_ms"] >= 0


@pytest.mark.asyncio
async def test_all_150_workflows_matrix_and_contracts():
    """Audits and validates the contractual execution of all 150 modular playbooks."""
    from scripts.verify_all_150_workflows import audit_and_test_all_150
    report = audit_and_test_all_150()
    assert report["total_workflows"] == 150
    assert report["passed"] == 150
    assert report["failed"] == 0
    assert report["overall_status"] == "PASS"


@pytest.mark.asyncio
async def test_20_attack_scenarios_execution():
    """Executes all 20 closed-loop defense and resilience scenarios."""
    from scripts.run_20_attack_scenarios import run_all_scenarios
    # Execute the async scenarios engine
    await run_all_scenarios()


@pytest.mark.asyncio
async def test_disaster_recovery_backup_and_parity():
    """Executes the full disaster recovery lifecycle: backup -> corrupt -> restore -> parity."""
    from scripts.disaster_recovery_test import run_disaster_recovery_test
    result = run_disaster_recovery_test()
    assert result is True



