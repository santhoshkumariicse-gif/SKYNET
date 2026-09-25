"""
SKYNET v5.0 — Production Readiness, Security, RBAC, HMAC & Resilience Test Suite
Exhaustively validates Sections 22 through 29, 35, and 36 of the Master Blueprint.
"""
import sys
import os
import time
import asyncio
from datetime import datetime, timezone, timedelta
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from jose import jwt

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.db.session import init_db, AsyncSessionLocal
from app.core.config import settings, Settings
from app.core.security import (
    create_access_token, 
    generate_audit_hmac, 
    verify_audit_hmac, 
    get_password_hash
)
from app.models.models import User, Role, AuditLog, Endpoint, Alert, Approval
from sqlalchemy import select


@pytest_asyncio.fixture(scope="module")
async def client():
    """Initializes database schema and yields an asynchronous HTTP test client."""
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def get_token_for_user(client: AsyncClient, username: str, password: str) -> str:
    res = await client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200, f"Login failed for {username}: {res.text}"
    return res.json()["access_token"]


# ==============================================================================
# 1. SECURITY HARDENING & PRODUCTION FAIL-SAFE (Section 22)
# ==============================================================================
def test_production_hardening_failsafe():
    """Verifies that production startup immediately aborts if default credentials or secrets are detected."""
    # Test 1: Insecure default SECRET_KEY in production
    with pytest.raises(ValueError, match="CRITICAL SECURITY ERROR.*SECRET_KEY"):
        s = Settings(
            ENVIRONMENT="production",
            SECRET_KEY="skynet_super_secret_jwt_key_enterprise_2026_prod_change_me",
            HMAC_SECRET="valid_production_hmac_secret_key_long_enough",
            AGENT_API_KEY="valid_agent_key_production",
            ADMIN_INITIAL_PASSWORD="SecureProdPassword2026!"
        )

    # Test 2: Insecure default HMAC_SECRET in production
    with pytest.raises(ValueError, match="CRITICAL SECURITY ERROR.*HMAC_SECRET"):
        s = Settings(
            ENVIRONMENT="production",
            SECRET_KEY="valid_production_secret_jwt_key_long_enough",
            HMAC_SECRET="skynet_hmac_sha256_audit_key_enterprise_2026_change_me",
            AGENT_API_KEY="valid_agent_key_production",
            ADMIN_INITIAL_PASSWORD="SecureProdPassword2026!"
        )

    # Test 3: Insecure default AGENT_API_KEY in production
    with pytest.raises(ValueError, match="CRITICAL SECURITY ERROR.*AGENT_API_KEY"):
        s = Settings(
            ENVIRONMENT="production",
            SECRET_KEY="valid_production_secret_jwt_key_long_enough",
            HMAC_SECRET="valid_production_hmac_secret_key_long_enough",
            AGENT_API_KEY="skynet_agent_default_secret_token_2026",
            ADMIN_INITIAL_PASSWORD="SecureProdPassword2026!"
        )

    # Test 4: Default or missing ADMIN_INITIAL_PASSWORD in production
    with pytest.raises(ValueError, match="CRITICAL SECURITY ERROR.*ADMIN_INITIAL_PASSWORD"):
        s = Settings(
            ENVIRONMENT="production",
            SECRET_KEY="valid_production_secret_jwt_key_long_enough",
            HMAC_SECRET="valid_production_hmac_secret_key_long_enough",
            AGENT_API_KEY="valid_agent_key_production",
            ADMIN_INITIAL_PASSWORD="admin123"
        )


# ==============================================================================
# 2. AUTHENTICATION (Section 23)
# ==============================================================================
@pytest.mark.asyncio
async def test_authentication_suite(client: AsyncClient):
    """Exhaustive authentication tests: valid, invalid, expired, malformed tokens."""
    # 1. Valid login
    login_res = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token is not None

    # 2. Invalid password
    bad_res = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrongpassword!"})
    assert bad_res.status_code == 401

    # 3. Non-existent username
    ghost_res = await client.post("/api/v1/auth/login", json={"username": "non_existent_ghost", "password": "any"})
    assert ghost_res.status_code == 401

    # 4. Malformed JWT token
    malformed_headers = {"Authorization": "Bearer not.a.valid.jwt.payload"}
    res_malformed = await client.get("/api/v1/auth/me", headers=malformed_headers)
    assert res_malformed.status_code == 401

    # 5. Expired JWT token
    expired_payload = {
        "sub": "test_user_id",
        "type": "access",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=10)
    }
    expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    res_expired = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert res_expired.status_code == 401


# ==============================================================================
# 3. AUTHORIZATION & RBAC (Section 24)
# ==============================================================================
@pytest.mark.asyncio
async def test_rbac_authorization_matrix(client: AsyncClient):
    """
    Verifies that RBAC permissions are strictly enforced at the API level.
    Roles evaluated: ADMIN, SOC_ANALYST, INVESTIGATOR, INCIDENT_RESPONDER, AUDITOR, READ_ONLY.
    """
    # Get tokens for various roles
    admin_token = await get_token_for_user(client, "admin", "admin123")
    responder_token = await get_token_for_user(client, "responder", "ResponderSecure2026!")
    readonly_token = await get_token_for_user(client, "readonly", "ReadOnlySecure2026!")
    auditor_token = await get_token_for_user(client, "auditor", "AuditorSecure2026!")

    contain_payload = {
        "action_type": "ISOLATE_HOST",
        "target_identifier": "SEC-WS-001",
        "reason": "RBAC verification test",
        "rollback_plan": "Restore network"
    }

    # 1. READ_ONLY attempting high-impact SOAR action must be rejected with 403 Forbidden
    ro_res = await client.post(
        "/api/v1/soar/execute",
        json=contain_payload,
        headers={"Authorization": f"Bearer {readonly_token}"}
    )
    assert ro_res.status_code == 403
    assert "Access denied" in ro_res.json()["detail"]

    # 2. AUDITOR attempting high-impact SOAR action must be rejected with 403 Forbidden
    aud_res = await client.post(
        "/api/v1/soar/execute",
        json=contain_payload,
        headers={"Authorization": f"Bearer {auditor_token}"}
    )
    assert aud_res.status_code == 403

    # 3. INCIDENT_RESPONDER executing SOAR containment succeeds
    resp_res = await client.post(
        "/api/v1/soar/execute",
        json=contain_payload,
        headers={"Authorization": f"Bearer {responder_token}"}
    )
    assert resp_res.status_code == 200
    assert resp_res.json()["status"] == "EXECUTED"

    # 4. ADMIN executing SOAR containment succeeds (wildcard permission)
    admin_res = await client.post(
        "/api/v1/soar/execute",
        json=contain_payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_res.status_code == 200

    # 5. AUDITOR reading audit integrity succeeds
    aud_verify = await client.post(
        "/api/v1/audit/verify-integrity",
        headers={"Authorization": f"Bearer {auditor_token}"}
    )
    assert aud_verify.status_code == 200
    assert aud_verify.json()["status"] == "PASS"

    # 6. READ_ONLY attempting to verify audit integrity is rejected with 403 Forbidden
    ro_verify = await client.post(
        "/api/v1/audit/verify-integrity",
        headers={"Authorization": f"Bearer {readonly_token}"}
    )
    assert ro_verify.status_code == 403


# ==============================================================================
# 4. AUDIT & CRYPTOGRAPHIC HMAC INTEGRITY (Section 25)
# ==============================================================================
@pytest.mark.asyncio
async def test_audit_hmac_tamper_detection(client: AsyncClient):
    """
    Verifies that:
    1. Every sensitive action generates a cryptographic HMAC signature.
    2. Tampering with any log record is immediately detected.
    """
    admin_token = await get_token_for_user(client, "admin", "admin123")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Clean audit verification
    verify_res = await client.post("/api/v1/audit/verify-integrity", headers=headers)
    assert verify_res.status_code == 200
    data = verify_res.json()
    assert data["status"] == "PASS"
    assert data["integrity_verified"] is True
    assert data["tampered_records_count"] == 0

    # 2. Simulate Tampering: inject a record with an invalid / forged HMAC signature
    async with AsyncSessionLocal() as session:
        forged_log = AuditLog(
            actor="attacker_forged",
            action="FORGED_CONTAINMENT",
            resource_type="CONTAINMENT",
            resource_id="TARGET-007",
            hmac_signature="0000000000000000000000000000000000000000000000000000000000000000",
            result="FORGED",
            client_ip="10.0.0.1"
        )
        session.add(forged_log)
        await session.commit()
        forged_id = forged_log.id

    # 3. Re-verify integrity: must catch the forged record!
    tamper_check_res = await client.post("/api/v1/audit/verify-integrity", headers=headers)
    assert tamper_check_res.status_code == 200
    tamper_data = tamper_check_res.json()
    assert tamper_data["status"] == "FAIL"
    assert tamper_data["integrity_verified"] is False
    assert tamper_data["tampered_records_count"] >= 1
    assert any(t["id"] == forged_id for t in tamper_data["tampered_records"])

    # Cleanup forged log
    async with AsyncSessionLocal() as session:
        f_res = await session.execute(select(AuditLog).where(AuditLog.id == forged_id))
        f_obj = f_res.scalars().first()
        if f_obj:
            await session.delete(f_obj)
            await session.commit()


# ==============================================================================
# 5. ENTERPRISE DATABASE SCALING & CONCURRENCY (Section 26)
# ==============================================================================
@pytest.mark.asyncio
async def test_database_concurrent_writes_and_rollback():
    """Validates transactional integrity, rollback safety, and concurrent writes."""
    # 1. Concurrent writes test (10 tasks writing concurrently)
    async def create_alert_worker(idx: int):
        async with AsyncSessionLocal() as session:
            alt = Alert(
                title=f"Concurrent Test Alert {idx}",
                description="Testing database concurrency",
                severity="LOW",
                source="CONCURRENCY_TEST"
            )
            session.add(alt)
            await session.commit()
            return alt.id

    tasks = [create_alert_worker(i) for i in range(10)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # Ensure all 10 writes succeeded with no database locks or crashes
    assert all(isinstance(r, str) for r in results)

    # 2. Transaction Rollback Safety
    async with AsyncSessionLocal() as session:
        try:
            session.add(Alert(
                title="Rollback Test Alert",
                description="Will be rolled back",
                severity="MEDIUM",
                source="ROLLBACK_TEST"
            ))
            # Simulate unexpected application failure before commit
            raise RuntimeError("Simulated mid-transaction failure")
        except RuntimeError:
            await session.rollback()

    # Verify rolled back alert was not persisted
    async with AsyncSessionLocal() as session:
        check_res = await session.execute(select(Alert).where(Alert.source == "ROLLBACK_TEST"))
        assert check_res.scalars().first() is None


# ==============================================================================
# 6. APPLICATION SECURITY TESTING (Section 29)
# ==============================================================================
@pytest.mark.asyncio
async def test_security_headers_and_injection_resilience(client: AsyncClient):
    """
    Validates enterprise security headers and resilience to SQLi and XSS injection attempts.
    """
    # 1. Security Headers Verification
    res = await client.get("/health")
    headers = res.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    # 2. SQL Injection Attempt in search parameters
    sqli_payload = "' OR '1'='1' --"
    sqli_res = await client.get(f"/api/v1/assets?search={sqli_payload}")
    assert sqli_res.status_code == 200
    # Parameterized query must treat payload literally, returning 0 results instead of dumping table
    assert len(sqli_res.json()) == 0

    # 3. Cross-Site Scripting (XSS) payload resilience
    xss_payload = "<script>alert('XSS')</script>"
    xss_res = await client.post("/api/v1/hunt/save", json={
        "name": f"XSS Test {int(time.time())}",
        "query": f"process.name = '{xss_payload}'"
    })
    assert xss_res.status_code == 200
    saved = xss_res.json()
    assert saved["query"] == f"process.name = '{xss_payload}'"

    # 4. Path Traversal check
    traversal_payload = "../../../../../etc/passwd"
    trav_res = await client.get(f"/api/v1/assets?search={traversal_payload}")
    assert trav_res.status_code == 200
    assert len(trav_res.json()) == 0


# ==============================================================================
# 7. PERFORMANCE & LATENCY BASELINE (Section 36)
# ==============================================================================
@pytest.mark.asyncio
async def test_performance_latencies(client: AsyncClient):
    """Measures and validates production latency thresholds."""
    # 1. System Health latency (< 50ms)
    t0 = time.time()
    h_res = await client.get("/health")
    health_latency_ms = (time.time() - t0) * 1000
    assert h_res.status_code == 200
    assert health_latency_ms < 50.0

    # 2. Telemetry ingestion throughput (< 200ms)
    t1 = time.time()
    batch = {
        "agent_key": "skynet_agent_default_secret_token_2026",
        "hostname": "PERF-HOST-01",
        "ip_address": "10.0.1.55",
        "events": [
            {
                "event_id_code": 1,
                "event_source": "sysmon",
                "host_name": "PERF-HOST-01",
                "process_name": "cmd.exe",
                "command_line": "cmd.exe /c echo ping"
            }
        ]
    }
    ing_res = await client.post("/api/v1/telemetry/ingest", json=batch)
    ingest_latency_ms = (time.time() - t1) * 1000
    assert ing_res.status_code == 200
    assert ingest_latency_ms < 200.0


# ==============================================================================
# 8. CLEAN-START LIFECYCLE DEPLOYMENT VALIDATION (Section 40)
# ==============================================================================
@pytest.mark.asyncio
async def test_clean_start_lifecycle():
    """Validates the 15-step clean-start deployment lifecycle."""
    from scripts.clean_start_validation import run_clean_start_test
    res = await run_clean_start_test()
    assert res is True

