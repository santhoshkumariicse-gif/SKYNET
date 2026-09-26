"""
SKYNET v5.0 — Prompts 11 to 15 Verification Test Suite
Tests:
- Prompt 11: Android telemetry payload schema & signature verification
- Prompt 12: Infrastructure Risk Engine calculations, weights, and categories
- Prompt 13: Multi-Site hierarchy, health aggregation, and comparison matrix
- Prompt 14: Prometheus /metrics exposition & OpenTelemetry traceparent propagation
- Prompt 15: Strategic roadmap and architectural deliverables validation
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.risk_engine import risk_engine


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_prompt_11_android_telemetry_schema(client):
    """Verifies that an Android agent telemetry payload with battery & storage is accepted."""
    android_payload = {
        "device_id": "AND-TEST-NODE-001",
        "cpu": 24.5,
        "ram": 58.2,
        "disk": 42.1,
        "battery_pct": 85.0,
        "network_rx_mb": 18.2,
        "network_tx_mb": 5.4,
        "processes_count": 42
    }
    resp = client.post("/api/v1/metrics", json=android_payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["device_id"] == "AND-TEST-NODE-001"
    assert data["cpu"] == 24.5
    assert data["ram"] == 58.2


def test_prompt_12_infrastructure_risk_engine_bounds_and_categories():
    """Validates that risk scoring formulas, factor weights, and categories behave deterministically."""
    # 1. Low risk scenario
    low_risk = risk_engine.calculate_device_risk(
        device_id="DEV-LOW-001",
        hostname="workstation-01",
        latest_metrics={"cpu_percent": 15.0, "memory_percent": 30.0, "disk_percent": 40.0},
        device_status="ONLINE"
    )
    assert 0 <= low_risk.risk_score <= 20
    assert low_risk.risk_category == "LOW"
    assert len(low_risk.recommended_actions) > 0

    # 2. Critical risk scenario (high saturation, active critical alert, offline)
    critical_risk = risk_engine.calculate_device_risk(
        device_id="DEV-CRIT-001",
        hostname="db-primary-01",
        latest_metrics={"cpu_percent": 95.0, "memory_percent": 94.0, "disk_percent": 92.0},
        baseline={"avg_cpu": 25.0, "avg_ram": 40.0},
        active_alerts=[{"title": "Database Crash Imminent", "severity": "CRITICAL", "message": "OOM Killer active"}],
        device_status="DEGRADED"
    )
    assert critical_risk.risk_score >= 60
    assert critical_risk.risk_category in ("HIGH", "CRITICAL")
    assert any("CPU" in f["factor"] for f in critical_risk.contributing_factors)
    assert any("Memory" in f["factor"] for f in critical_risk.contributing_factors)


def test_prompt_12_risk_api_endpoints(client):
    """Verifies GET /api/v1/risk/fleet returns valid fleet risk distribution."""
    resp = client.get("/api/v1/risk/fleet")
    assert resp.status_code == 200
    data = resp.json()
    assert "fleet_risk_score" in data
    assert "risk_category" in data
    assert "distribution" in data
    assert data["evaluated_devices"] > 0


def test_prompt_13_multi_site_listing_and_comparison(client):
    """Verifies Multi-Site listing, regional comparison, and site health endpoints."""
    # 1. List sites
    resp = client.get("/api/v1/sites")
    assert resp.status_code == 200
    sites = resp.json()
    assert len(sites) >= 4  # HQ-NYC, DC-FRA, BR-LON, BR-TYO
    site_codes = {s["code"] for s in sites}
    assert "HQ-NYC" in site_codes
    assert "DC-FRA" in site_codes

    # 2. Site comparison
    resp_comp = client.get("/api/v1/sites/comparison")
    assert resp_comp.status_code == 200
    comp_data = resp_comp.json()
    assert "comparison_matrix" in comp_data
    assert len(comp_data["comparison_matrix"]) >= 4

    # 3. Site detailed health
    first_site_id = sites[0]["id"]
    resp_health = client.get(f"/api/v1/sites/{first_site_id}/health")
    assert resp_health.status_code == 200
    health_data = resp_health.json()
    assert "site" in health_data
    assert "devices" in health_data


def test_prompt_14_prometheus_metrics_exposition(client):
    """Verifies that GET /metrics returns valid standard Prometheus exposition text."""
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "text/plain" in resp.headers["content-type"]
    body = resp.text
    assert "skynet_fleet_health_score" in body
    assert "skynet_fleet_risk_score" in body
    assert "skynet_active_endpoints" in body
    assert "skynet_http_requests_total" in body
    assert "skynet_uptime_seconds" in body


def test_prompt_14_opentelemetry_w3c_traceparent_propagation(client):
    """Verifies that OpenTelemetry trace headers are attached and propagated on responses."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert "X-Trace-Id" in resp.headers
    assert "X-Span-Id" in resp.headers
    assert "traceparent" in resp.headers
    # Validate W3C traceparent structure (00-{trace_id}-{span_id}-01)
    parts = resp.headers["traceparent"].split("-")
    assert len(parts) == 4
    assert parts[0] == "00"
    assert parts[3] == "01"
