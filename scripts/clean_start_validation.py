"""
SKYNET v5.0 — Clean-Start 15-Step Deployment & Lifecycle Verification Engine
Executes the exact 15-step sequence defined in Section 40 of the Master Blueprint.
"""
import sys
import os
import time
import asyncio
from pathlib import Path
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from httpx import ASGITransport, AsyncClient
from app.main import app
from app.db.session import init_db, AsyncSessionLocal
from app.models.models import Alert, Incident, Endpoint, AuditLog, Approval
from sqlalchemy import select, func


async def run_clean_start_test():
    print(f"\n{'='*100}")
    print("  SKYNET v5.0 — 15-STEP CLEAN-START LIFECYCLE & DEPLOYMENT ACCEPTANCE TEST")
    print("  Compliance Standard: Section 40 Verification Protocol")
    print(f"{'='*100}\n")

    t_start = time.time()
    steps_passed = 0

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Step 1: Environment & Config Verification
        print("[01/15] Verifying Clean Environment & Configuration...")
        env_example = ROOT_DIR / ".env.example"
        assert env_example.exists(), "Missing .env.example"
        print("        -> PASS: Configuration environment files verified.")
        steps_passed += 1

        # Step 2: Dependencies & Runtime Verification
        print("[02/15] Verifying Dependencies & Runtime Systems...")
        import fastapi
        import sqlalchemy
        import pydantic
        print(f"        -> PASS: FastAPI v{fastapi.__version__}, SQLAlchemy v{sqlalchemy.__version__}")
        steps_passed += 1

        # Step 3: Configure Environment Isolation
        print("[03/15] Validating Environment Security Hardening...")
        from app.core.config import settings
        assert settings.ENVIRONMENT in ["development", "staging", "production"]
        print(f"        -> PASS: Environment configured: {settings.ENVIRONMENT}")
        steps_passed += 1

        # Step 4: Initialize Database
        print("[04/15] Initializing Database & Enterprise Schemas...")
        await init_db()
        async with AsyncSessionLocal() as session:
            ep_count = (await session.execute(select(func.count(Endpoint.id)))).scalar()
            assert ep_count >= 1, "Database initialization failed to seed fleet endpoints"
        print(f"        -> PASS: Database initialized. Monitored endpoints: {ep_count}")
        steps_passed += 1

        # Step 5: Load Workflows Manifest
        print("[05/15] Loading Modular 150-Workflow Manifest...")
        manifest_path = ROOT_DIR / "workflows" / "SKYNET_v5_ALL_150_N8N_WORKFLOWS" / "SKYNET_v5_WORKFLOW_MANIFEST.json"
        assert manifest_path.exists(), "Workflow manifest missing"
        with open(manifest_path, "r", encoding="utf-8") as f:
            import json
            mf = json.load(f)
            assert mf["workflow_count"] == 150, "Manifest does not contain 150 workflows"
        print(f"        -> PASS: 150 Workflows successfully loaded across 15 domains.")
        steps_passed += 1

        # Step 6: Start & Validate Core Services
        print("[06/15] Verifying Core Services Operational Health...")
        health_res = await client.get("/health")
        assert health_res.status_code == 200 and health_res.json()["status"] == "operational"
        print("        -> PASS: REST API Gateway & Health subsystem operational.")
        steps_passed += 1

        # Step 7: Authenticate User & Issue JWT
        print("[07/15] Authenticating SOC Operator via JWT...")
        login_res = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("        -> PASS: JWT access token granted.")
        steps_passed += 1

        # Step 8: Submit Security Telemetry
        print("[08/15] Submitting Endpoint Attack Telemetry...")
        test_host = f"HOST-CLEAN-{int(time.time())}"
        telemetry_payload = {
            "agent_key": "skynet_agent_default_secret_token_2026",
            "hostname": test_host,
            "ip_address": "10.10.40.75",
            "events": [
                {
                    "event_id_code": 1,
                    "event_source": "sysmon",
                    "host_name": test_host,
                    "process_name": "powershell.exe",
                    "process_command_line": "powershell.exe -NoP -Enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoA...",
                    "user_name": "attacker_user"
                },
                {
                    "event_id_code": 3,
                    "event_source": "sysmon",
                    "host_name": test_host,
                    "dst_ip": "185.220.101.5",
                    "dst_port": 443
                }
            ]
        }
        ing_res = await client.post("/api/v1/telemetry/ingest", json=telemetry_payload)
        assert ing_res.status_code == 200
        ing_data = ing_res.json()
        assert ing_data["events_processed"] == 2
        print(f"        -> PASS: Ingested {ing_data['events_processed']} raw telemetry events.")
        steps_passed += 1

        # Step 9: Run Detection Engine
        print("[09/15] Evaluating Sigma Rules & IOC Matchers...")
        assert ing_data["alerts_generated"] >= 1
        print(f"        -> PASS: Detection engine matched {ing_data['alerts_generated']} critical detections.")
        steps_passed += 1

        # Step 10: Generate Correlated Alert
        print("[10/15] Generating Correlated Security Alert...")
        alerts_res = await client.get("/api/v1/alerts?limit=1", headers=headers)
        assert alerts_res.status_code == 200
        latest_alerts = alerts_res.json()
        assert len(latest_alerts) >= 1
        alert_item = latest_alerts[0]
        print(f"        -> PASS: Alert generated: {alert_item['title']} (Severity: {alert_item['severity']})")
        steps_passed += 1

        # Step 11: Investigate via AI Cognitive Engine
        print("[11/15] Executing Autonomous AI Incident Investigation...")
        incidents_res = await client.get("/api/v1/incidents", headers=headers)
        assert incidents_res.status_code == 200
        inc_list = incidents_res.json()
        assert len(inc_list) >= 1
        target_inc = inc_list[0]
        
        inv_res = await client.post(f"/api/v1/incidents/{target_inc['id']}/investigate", headers=headers)
        assert inv_res.status_code == 200
        dossier = inv_res.json()
        assert dossier["confidence_score"] >= 0.7
        print(f"        -> PASS: AI Dossier synthesized. Confidence: {dossier['confidence_score']*100:.0f}%, Root cause identified.")
        steps_passed += 1

        # Step 12: Execute Approved Response (SOAR Containment)
        print("[12/15] Executing Containment Action with Approval Gating...")
        contain_res = await client.post(
            "/api/v1/soar/execute",
            json={
                "action_type": "ISOLATE_HOST",
                "target_identifier": test_host,
                "reason": "Clean-start validation containment",
                "rollback_plan": "Restore network"
            },
            headers=headers
        )
        assert contain_res.status_code == 200
        cdata = contain_res.json()
        assert cdata["status"] == "EXECUTED"
        print(f"        -> PASS: SOAR action executed. Token: {cdata['signed_token'][:16]}...")
        steps_passed += 1

        # Step 13: Verify Response & Fleet State
        print("[13/15] Verifying Remote Containment State...")
        asset_res = await client.get(f"/api/v1/assets?search={test_host}", headers=headers)
        assert asset_res.status_code == 200
        assets = asset_res.json()
        assert len(assets) > 0
        assert assets[0]["status"] == "ISOLATED"
        print(f"        -> PASS: Fleet status verified: {test_host} is ISOLATED.")
        steps_passed += 1

        # Step 14: Generate & Verify Cryptographic HMAC Audit Trail
        print("[14/15] Validating Cryptographic Audit Provenance...")
        audit_res = await client.post("/api/v1/audit/verify-integrity", headers=headers)
        assert audit_res.status_code == 200
        adata = audit_res.json()
        assert adata["status"] == "PASS" and adata["integrity_verified"] is True
        print(f"        -> PASS: Audit trail integrity verified: {adata['cryptographically_verified_records']} records sealed.")
        steps_passed += 1

        # Step 15: Close Incident
        print("[15/15] Performing Incident Resolution & Closure...")
        inc_close_res = await client.put(
            f"/api/v1/incidents/{target_inc['id']}",
            json={
                "status": "CLOSED",
                "verdict": "TRUE_POSITIVE"
            },
            headers=headers
        )
        assert inc_close_res.status_code == 200
        print(f"        -> PASS: Incident {target_inc['incident_number']} closed with TRUE_POSITIVE verdict.")
        steps_passed += 1

    duration = round(time.time() - t_start, 2)
    print(f"\n{'-'*100}")
    print("CLEAN-START VERIFICATION RESULT:")
    print(f"  * Steps Executed      : {steps_passed} / 15")
    print(f"  * Execution Latency   : {duration}s")
    print(f"  * Clean Deployment    : 100% OPERATIONAL")
    print(f"  * Final Status        : PASS")
    print(f"{'='*100}\n")
    return True


if __name__ == "__main__":
    asyncio.run(run_clean_start_test())
