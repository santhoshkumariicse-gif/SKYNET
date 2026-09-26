"""
SKYNET v5.0 — Prompt 5 & Prompt 6 Test Suite: RAG Knowledge Engine & Security Hardening
Tests:
- RAG Document Ingestion & Chunking
- RAG Semantic Query & Citation Accuracy
- RAG Prompt Guardrails (Refusal on unindexed knowledge)
- JWT Token Refresh & Token Expiry
- Device Identity Enrollment & Fingerprinting
- Device HMAC Signature Verification
- Cryptographic Replay Attack Mitigation
"""
import pytest
import hmac
import hashlib
from datetime import datetime, timezone, timedelta
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.rag.rag_engine import rag_engine
from app.rag.vector_store import local_vector_store


@pytest.mark.asyncio
async def test_rag_knowledge_initialization():
    """Verify default runbooks and post-mortems are indexed."""
    indexed = await rag_engine.initialize_default_knowledge_base()
    docs = local_vector_store.list_documents()
    assert len(docs) >= 3
    doc_ids = [d["doc_id"] for d in docs]
    assert any("outage" in d for d in doc_ids)
    assert any("restart" in d for d in doc_ids)
    assert any("memory" in d for d in doc_ids)


@pytest.mark.asyncio
async def test_rag_query_with_citations():
    """Verify semantic queries return factual answers with strict citations."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Query 1: Outage
        res1 = await client.post("/api/v1/rag/query", json={"query": "What caused yesterday's outage?", "top_k": 3})
        assert res1.status_code == 200
        data1 = res1.json()
        assert len(data1["citations"]) >= 1
        assert "post-mortem" in data1["citations"][0]["doc_title"].lower() or "outage" in data1["citations"][0]["doc_title"].lower()
        assert data1["confidence"] > 0.3

        # Query 2: Restart agent
        res2 = await client.post("/api/v1/rag/query", json={"query": "How do I restart the monitoring agent?", "top_k": 3})
        assert res2.status_code == 200
        data2 = res2.json()
        assert len(data2["citations"]) >= 1
        assert "restart" in data2["citations"][0]["doc_title"].lower() or "runbook" in data2["citations"][0]["doc_title"].lower()


@pytest.mark.asyncio
async def test_rag_guardrail_refusal_for_unknown_knowledge():
    """Verify guardrails prevent hallucination when knowledge is not in the repository."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/v1/rag/query", json={"query": "What is the secret recipe for Martian blueberry pie?", "top_k": 3})
        assert res.status_code == 200
        data = res.json()
        assert "no verified record" in data["answer"].lower() or "withheld" in data["answer"].lower()
        assert data["confidence"] == 0.0


@pytest.mark.asyncio
async def test_rag_custom_document_ingestion_and_deletion():
    """Verify dynamic document ingestion and deletion via API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        doc_payload = {
            "title": "Quantum Encryption Protocol Runbook",
            "content": "# Quantum Protocols\n\nTo rotate the post-quantum lattice keys, run `skynet-cli keys rotate --algorithm Kyber1024`.\n\n## Verification\nConfirm key fingerprint using `skynet-cli keys verify`.",
            "doc_type": "runbook",
            "doc_id": "doc_quantum_keys",
            "tags": ["crypto", "runbook"]
        }
        ingest_res = await client.post("/api/v1/rag/ingest", json=doc_payload)
        assert ingest_res.status_code == 201
        assert ingest_res.json()["chunks_ingested"] >= 1

        # Query the newly ingested runbook
        query_res = await client.post("/api/v1/rag/query", json={"query": "How to rotate post-quantum lattice keys?", "top_k": 2})
        assert query_res.status_code == 200
        q_data = query_res.json()
        assert any("Kyber1024" in c["snippet"] for c in q_data["citations"])

        # Delete the document
        del_res = await client.delete("/api/v1/rag/documents/doc_quantum_keys")
        assert del_res.status_code == 200


@pytest.mark.asyncio
async def test_jwt_token_refresh_flow():
    """Verify refresh token exchange and invalid token rejection."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login
        login_res = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
        assert login_res.status_code == 200
        tokens = login_res.json()
        refresh_token = tokens["refresh_token"]

        # Exchange refresh token
        ref_res = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert ref_res.status_code == 200
        new_tokens = ref_res.json()
        assert new_tokens["access_token"] is not None
        assert new_tokens["token_type"] == "bearer"

        # Rejection of bogus refresh token
        bad_res = await client.post("/api/v1/auth/refresh", json={"refresh_token": "tampered.jwt.payload"})
        assert bad_res.status_code == 401


@pytest.mark.asyncio
async def test_cryptographic_device_enrollment_and_verification():
    """Verify agent cryptographic enrollment, hardware fingerprinting, and replay prevention."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Enroll device
        enroll_res = await client.post("/api/v1/auth/device-enroll", json={
            "hostname": "SECURE-EDGE-NODE-01",
            "hardware_fingerprint": "HW-CPU-INTEL-9941-MB-8842",
            "os_name": "Windows 11 Enterprise",
            "mac_address": "00:1B:44:11:3A:B7",
            "ip_address": "10.0.8.44"
        })
        assert enroll_res.status_code == 200
        enroll_data = enroll_res.json()
        device_id = enroll_data["device_id"]
        hmac_secret = enroll_data["hmac_secret"]

        # 2. Generate valid signed heartbeat
        now_ts = datetime.now(timezone.utc).isoformat()
        valid_sig = hmac.new(hmac_secret.encode(), f"{device_id}:{now_ts}".encode(), hashlib.sha256).hexdigest()

        verify_res = await client.post("/api/v1/auth/verify-device-identity", json={
            "device_id": device_id,
            "timestamp": now_ts,
            "signature": valid_sig,
            "hardware_fingerprint": "HW-CPU-INTEL-9941-MB-8842"
        })
        assert verify_res.status_code == 200
        assert verify_res.json()["status"] == "VERIFIED"

        # 3. Test Replay Attack Mitigation (Expired timestamp > 300s)
        expired_ts = (datetime.now(timezone.utc) - timedelta(seconds=600)).isoformat()
        expired_sig = hmac.new(hmac_secret.encode(), f"{device_id}:{expired_ts}".encode(), hashlib.sha256).hexdigest()

        replay_res = await client.post("/api/v1/auth/verify-device-identity", json={
            "device_id": device_id,
            "timestamp": expired_ts,
            "signature": expired_sig,
            "hardware_fingerprint": "HW-CPU-INTEL-9941-MB-8842"
        })
        assert replay_res.status_code == 401
        assert "replay" in replay_res.json()["detail"].lower()

        # 4. Test Metric Tampering / Fake Signature
        tamper_res = await client.post("/api/v1/auth/verify-device-identity", json={
            "device_id": device_id,
            "timestamp": now_ts,
            "signature": "bogus_tampered_signature_hex",
            "hardware_fingerprint": "HW-CPU-INTEL-9941-MB-8842"
        })
        assert tamper_res.status_code == 401
