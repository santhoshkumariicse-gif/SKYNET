"""
SKYNET v5.0 — Infrastructure Risk Engine API
Endpoints:
- GET /risk/fleet
- GET /risk/devices/{id}
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.models import Endpoint, Metric, Baseline, Alert
from app.services.risk_engine import risk_engine

router = APIRouter(prefix="/risk", tags=["Infrastructure Risk Engine"])


@router.get("/fleet")
async def get_fleet_risk(db: AsyncSession = Depends(get_db)):
    """
    Computes global fleet risk score, risk distribution, and identifies
    highest-risk infrastructure nodes with actionable remediation steps.
    """
    endpoints_res = await db.execute(select(Endpoint))
    endpoints = endpoints_res.scalars().all()

    if not endpoints:
        return {
            "fleet_risk_score": 0,
            "risk_category": "LOW",
            "evaluated_devices": 0,
            "distribution": {"CRITICAL": 0, "HIGH": 0, "ELEVATED": 0, "MODERATE": 0, "LOW": 0},
            "highest_risk_devices": []
        }

    device_assessments = []
    distribution = {"CRITICAL": 0, "HIGH": 0, "ELEVATED": 0, "MODERATE": 0, "LOW": 0}

    for ep in endpoints:
        # Fetch latest metric
        metric_res = await db.execute(
            select(Metric)
            .where(Metric.device_id == ep.id)
            .order_by(Metric.timestamp.desc())
            .limit(1)
        )
        latest_metric = metric_res.scalar_one_or_none()
        m_dict = {
            "cpu_percent": latest_metric.cpu if latest_metric else (ep.cpu_usage or 15.0),
            "memory_percent": latest_metric.ram if latest_metric else (ep.memory_usage or 40.0),
            "disk_percent": latest_metric.disk if latest_metric else (ep.disk_usage or 50.0),
            "network_percent": 25.0
        }

        # Fetch baseline
        base_res = await db.execute(
            select(Baseline).where(Baseline.device_id == ep.id)
        )
        base = base_res.scalar_one_or_none()
        b_dict = {
            "avg_cpu": base.avg_cpu if base else 20.0,
            "avg_ram": base.avg_ram if base else 45.0
        }

        # Fetch active alerts
        alerts_res = await db.execute(
            select(Alert)
            .where(Alert.device_id == ep.id, Alert.status == "ACTIVE")
            .limit(5)
        )
        alerts = [
            {"title": a.title, "severity": a.severity, "message": a.message}
            for a in alerts_res.scalars().all()
        ]

        assessment = risk_engine.calculate_device_risk(
            device_id=ep.id,
            hostname=ep.hostname,
            latest_metrics=m_dict,
            baseline=b_dict,
            active_alerts=alerts,
            device_status=ep.status
        )
        assessment_dict = assessment.to_dict()
        device_assessments.append(assessment_dict)
        distribution[assessment.risk_category] = distribution.get(assessment.risk_category, 0) + 1

    device_assessments.sort(key=lambda x: x["risk_score"], reverse=True)
    avg_fleet_risk = round(sum(d["risk_score"] for d in device_assessments) / len(device_assessments))

    if avg_fleet_risk >= 80:
        cat = "CRITICAL"
    elif avg_fleet_risk >= 60:
        cat = "HIGH"
    elif avg_fleet_risk >= 40:
        cat = "ELEVATED"
    elif avg_fleet_risk >= 20:
        cat = "MODERATE"
    else:
        cat = "LOW"

    return {
        "fleet_risk_score": avg_fleet_risk,
        "risk_category": cat,
        "evaluated_devices": len(device_assessments),
        "distribution": distribution,
        "highest_risk_devices": device_assessments[:5]
    }


@router.get("/devices/{device_id}")
async def get_device_risk(device_id: str, db: AsyncSession = Depends(get_db)):
    """
    Computes a granular, explainable risk profile for an individual device,
    including mathematical sub-score decomposition and mitigating actions.
    """
    ep_res = await db.execute(select(Endpoint).where(Endpoint.id == device_id))
    ep = ep_res.scalar_one_or_none()
    if not ep:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device '{device_id}' not found in registry."
        )

    metric_res = await db.execute(
        select(Metric)
        .where(Metric.device_id == ep.id)
        .order_by(Metric.timestamp.desc())
        .limit(1)
    )
    latest_metric = metric_res.scalar_one_or_none()
    m_dict = {
        "cpu_percent": latest_metric.cpu if latest_metric else (ep.cpu_usage or 20.0),
        "memory_percent": latest_metric.ram if latest_metric else (ep.memory_usage or 45.0),
        "disk_percent": latest_metric.disk if latest_metric else (ep.disk_usage or 55.0),
        "network_percent": 15.0
    }

    base_res = await db.execute(select(Baseline).where(Baseline.device_id == ep.id))
    base = base_res.scalar_one_or_none()
    b_dict = {
        "avg_cpu": base.avg_cpu if base else 22.0,
        "avg_ram": base.avg_ram if base else 42.0
    }

    alerts_res = await db.execute(
        select(Alert).where(Alert.device_id == ep.id, Alert.status == "ACTIVE")
    )
    alerts = [
        {"title": a.title, "severity": a.severity, "message": a.message}
        for a in alerts_res.scalars().all()
    ]

    assessment = risk_engine.calculate_device_risk(
        device_id=ep.id,
        hostname=ep.hostname,
        latest_metrics=m_dict,
        baseline=b_dict,
        active_alerts=alerts,
        device_status=ep.status
    )

    return assessment.to_dict()
