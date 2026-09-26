"""
SKYNET Phase-1 Core Integration & API Tests
Validates all mandatory endpoints:
- POST /devices/register
- POST /metrics
- GET /devices
- GET /devices/{id}
- GET /metrics
- GET /health
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import sys
import os

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app
from app.core.config import settings
from app.db.session import init_db


@pytest_asyncio.fixture
async def client():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Verifies GET /health endpoint."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "operational"
    assert "SKYNET" in data["platform"]


@pytest.mark.asyncio
async def test_device_registration_and_query(client: AsyncClient):
    """Verifies POST /devices/register, GET /devices, and GET /devices/{id}."""
    test_device = {
        "id": "DEV-TEST-WIN-001",
        "hostname": "TEST-RIG-01",
        "ip_address": "192.168.10.15",
        "os_name": "Windows",
        "os_version": "11 Pro (22631)",
        "device_type": "Workstation",
        "cpu_cores": 8,
        "total_ram_mb": 16384.0,
        "total_disk_gb": 512.0,
        "agent_version": "5.0.0",
        "tags": ["ci", "test"]
    }

    # 1. Register device
    reg_resp = await client.post(
        "/devices/register",
        json=test_device,
        headers={"X-Agent-Key": settings.AGENT_API_KEY}
    )
    assert reg_resp.status_code == 201, reg_resp.text
    reg_data = reg_resp.json()
    assert reg_data["id"] == "DEV-TEST-WIN-001"
    assert reg_data["hostname"] == "TEST-RIG-01"
    assert reg_data["status"] == "ONLINE"

    # 2. List devices
    list_resp = await client.get("/devices")
    assert list_resp.status_code == 200
    devices = list_resp.json()
    assert any(d["id"] == "DEV-TEST-WIN-001" for d in devices)

    # 3. Get single device
    get_resp = await client.get("/devices/DEV-TEST-WIN-001")
    assert get_resp.status_code == 200
    device_data = get_resp.json()
    assert device_data["hostname"] == "TEST-RIG-01"
    assert device_data["ip_address"] == "192.168.10.15"


@pytest.mark.asyncio
async def test_metrics_ingestion_and_retrieval(client: AsyncClient):
    """Verifies POST /metrics and GET /metrics."""
    metric_payload = {
        "device_id": "DEV-TEST-WIN-001",
        "hostname": "TEST-RIG-01",
        "cpu": 45.2,
        "ram": 62.8,
        "gpu": 15.0,
        "disk": 52.4,
        "network": 2.45,
        "network_rx_mb": 1.80,
        "network_tx_mb": 0.65,
        "processes_count": 142,
        "battery_pct": 100.0,
        "raw_vitals": {"clock_mhz": 3400}
    }

    # Ingest metrics
    post_resp = await client.post(
        "/metrics",
        json=metric_payload,
        headers={"X-Agent-Key": settings.AGENT_API_KEY}
    )
    assert post_resp.status_code == 201, post_resp.text
    post_data = post_resp.json()
    assert post_data["device_id"] == "DEV-TEST-WIN-001"
    assert post_data["cpu"] == 45.2

    # Query metrics
    get_resp = await client.get("/metrics?device_id=DEV-TEST-WIN-001")
    assert get_resp.status_code == 200
    metrics_list = get_resp.json()
    assert len(metrics_list) >= 1
    assert metrics_list[0]["device_id"] == "DEV-TEST-WIN-001"


@pytest.mark.asyncio
async def test_agent_authentication_security(client: AsyncClient):
    """Verifies that invalid X-Agent-Key headers are rejected with 403 Forbidden."""
    bad_payload = {
        "hostname": "ROGUE-PC",
        "ip_address": "10.0.0.99",
        "os_name": "Windows"
    }

    resp = await client.post(
        "/devices/register",
        json=bad_payload,
        headers={"X-Agent-Key": "invalid_unauthorized_key"}
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_phase2_historical_metrics_and_trends(client: AsyncClient):
    """Verifies GET /metrics/history and GET /metrics/trends across time ranges."""
    # 1. Test history with 24h
    hist_resp = await client.get("/metrics/history?range=24h&points=20")
    assert hist_resp.status_code == 200
    hist_data = hist_resp.json()
    assert hist_data["range"] == "24h"
    assert len(hist_data["data"]) == 20
    assert "cpu" in hist_data["data"][0]
    assert "ram" in hist_data["data"][0]

    # 2. Test trends aggregation
    trend_resp = await client.get("/metrics/trends?range=24h")
    assert trend_resp.status_code == 200
    trend_data = trend_resp.json()
    assert "fleet_health_score" in trend_data
    assert "device_summary" in trend_data
    assert "trends" in trend_data
    assert "cpu" in trend_data["trends"]
    assert "max" in trend_data["trends"]["cpu"]


@pytest.mark.asyncio
async def test_phase2_device_history_filters(client: AsyncClient):
    """Verifies GET /devices/{id}/history with 1h, 24h, 7d, 30d filters."""
    for tr in ["1h", "24h", "7d", "30d"]:
        resp = await client.get(f"/devices/DEV-TEST-WIN-001/history?range={tr}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["range"] == tr
        assert data["device"]["hostname"] == "TEST-RIG-01"
        assert len(data["series"]) > 0
        assert "avg_cpu" in data["summary"]
        assert "avg_ram" in data["summary"]


@pytest.mark.asyncio
async def test_phase2_alert_thresholds_and_acknowledgement(client: AsyncClient):
    """Verifies automatic alert trigger on threshold breach (>90%) and acknowledgment."""
    high_cpu_payload = {
        "device_id": "DEV-TEST-WIN-001",
        "hostname": "TEST-RIG-01",
        "cpu": 96.5,
        "ram": 92.0,
        "gpu": 91.0,
        "disk": 94.0,
        "network": 5.2
    }

    # Ingest breach metrics
    ingest_resp = await client.post(
        "/metrics",
        json=high_cpu_payload,
        headers={"X-Agent-Key": settings.AGENT_API_KEY}
    )
    assert ingest_resp.status_code == 201

    # Query alerts for device
    alerts_resp = await client.get("/alerts?device_id=DEV-TEST-WIN-001")
    assert alerts_resp.status_code == 200
    alerts = alerts_resp.json()
    assert len(alerts) >= 1

    alert_to_ack = alerts[0]
    alert_id = alert_to_ack["id"]

    # Acknowledge alert
    ack_resp = await client.post(f"/alerts/{alert_id}/acknowledge")
    assert ack_resp.status_code == 200
    ack_data = ack_resp.json()
    assert ack_data["acknowledged"] is True
    assert ack_data["status"] == "ACKNOWLEDGED"


@pytest.mark.asyncio
async def test_phase3_health_score_breakdown(client: AsyncClient):
    """Verifies GET /health-score multi-factor health calculations."""
    resp = await client.get("/health-score")
    assert resp.status_code == 200
    data = resp.json()
    assert "fleet_health_score" in data
    assert "status_distribution" in data
    assert "devices" in data
    assert len(data["devices"]) > 0
    dev = data["devices"][0]
    assert "factors" in dev["health"]
    assert "cpu" in dev["health"]["factors"]
    assert "availability" in dev["health"]["factors"]


@pytest.mark.asyncio
async def test_phase3_anomalies_and_device_insights(client: AsyncClient):
    """Verifies GET /anomalies and GET /device-insights/{id} with natural language explanation."""
    # 1. Device insights
    insights_resp = await client.get("/device-insights/DEV-TEST-WIN-001")
    assert insights_resp.status_code == 200
    insights = insights_resp.json()
    assert insights["device_id"] == "DEV-TEST-WIN-001"
    assert "natural_language_summary" in insights
    assert "investigation_breakdown" in insights
    assert "facts" in insights["investigation_breakdown"]
    assert "hypotheses" in insights["investigation_breakdown"]
    assert "evidence" in insights["investigation_breakdown"]

    # 2. Anomalies list
    anom_resp = await client.get("/anomalies")
    assert anom_resp.status_code == 200
    assert isinstance(anom_resp.json(), list)


@pytest.mark.asyncio
async def test_phase4_copilot_natural_language_queries(client: AsyncClient):
    """Verifies POST /copilot/query RAG assistant."""
    queries = [
        "Why is TEST-RIG-01 slow?",
        "Show unhealthy devices.",
        "What is the general status of the fleet?"
    ]
    for q in queries:
        resp = await client.post("/copilot/query", json={"query": q})
        assert resp.status_code == 200
        data = resp.json()
        assert data["query"] == q
        assert len(data["answer"]) > 20
        assert "suggested_followups" in data
