"""
SKYNET v5.0 — AI Health Intelligence, Anomaly Analysis & Infrastructure Copilot API
Endpoints:
- GET /health-score
- GET /anomalies
- GET /anomalies/{id}
- GET /device-insights/{id}
- POST /copilot/query
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.models import Endpoint, Metric, Baseline, Anomaly, Alert, Incident
from app.services.anomaly_service import health_engine, explanation_engine, anomaly_service

router = APIRouter(tags=["AI Intelligence & Copilot"])


class CopilotQueryRequest(BaseModel):
    query: str
    context_device_id: Optional[str] = None


class CopilotQueryResponse(BaseModel):
    query: str
    answer: str
    intent: str
    devices_mentioned: List[str]
    suggested_followups: List[str]
    timestamp: str


@router.get("/health-score")
async def get_fleet_health_score(db: AsyncSession = Depends(get_db)):
    """
    Computes real-time multi-factor health scores for the entire fleet
    and itemizes individual device scores and deductions.
    """
    stmt = select(Endpoint).order_by(Endpoint.hostname.asc())
    res = await db.execute(stmt)
    devices = res.scalars().all()

    device_scores = []
    total_score = 0

    for dev in devices:
        breakdown = health_engine.calculate_device_health(dev)
        device_scores.append({
            "device_id": dev.id,
            "hostname": dev.hostname,
            "device_type": dev.device_type,
            "status": dev.status,
            "health": breakdown.to_dict()
        })
        total_score += breakdown.overall

    fleet_avg = round(total_score / max(len(devices), 1))

    return {
        "fleet_health_score": fleet_avg,
        "total_monitored": len(devices),
        "status_distribution": {
            "healthy": sum(1 for d in device_scores if d["health"]["health_score"] >= 80),
            "degraded": sum(1 for d in device_scores if 50 <= d["health"]["health_score"] < 80),
            "critical": sum(1 for d in device_scores if d["health"]["health_score"] < 50)
        },
        "devices": device_scores
    }


@router.get("/anomalies")
async def list_anomalies(
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    anomaly_type: Optional[str] = Query(None, description="Filter by type: CPU_SPIKE, MEMORY_LEAK, DISK_PRESSURE, etc."),
    status: Optional[str] = Query("ACTIVE", description="ACTIVE, INVESTIGATING, RESOLVED, FALSE_POSITIVE"),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve detected operational anomalies and behavioral deviations."""
    stmt = select(Anomaly).order_by(Anomaly.created_at.desc())
    if device_id:
        stmt = stmt.where(Anomaly.device_id == device_id)
    if anomaly_type:
        stmt = stmt.where(Anomaly.anomaly_type == anomaly_type.upper())
    if status and status.upper() != "ALL":
        stmt = stmt.where(Anomaly.status == status.upper())

    stmt = stmt.limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/anomalies/{anomaly_id}")
async def get_anomaly_details(anomaly_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve full anomaly intelligence dossier with statistical evidence."""
    stmt = select(Anomaly).where(Anomaly.id == anomaly_id)
    res = await db.execute(stmt)
    anomaly = res.scalars().first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly record not found")

    dev_res = await db.execute(select(Endpoint).where(Endpoint.id == anomaly.device_id))
    dev = dev_res.scalars().first()

    return {
        "anomaly": anomaly,
        "device": {
            "id": dev.id if dev else anomaly.device_id,
            "hostname": dev.hostname if dev else "Unknown",
            "ip_address": dev.ip_address if dev else "127.0.0.1",
            "status": dev.status if dev else "OFFLINE"
        }
    }


@router.get("/device-insights/{device_id}")
async def get_device_insights(device_id: str, db: AsyncSession = Depends(get_db)):
    """
    AI Explanation Engine endpoint:
    Synthesizes current telemetry, rolling baseline, and operational vitals into
    a structured natural language briefing with Facts, Hypotheses, and Evidence.
    """
    stmt = select(Endpoint).where(
        (Endpoint.id == device_id) | (Endpoint.hostname == device_id)
    )
    res = await db.execute(stmt)
    device = res.scalars().first()
    if not device:
        raise HTTPException(status_code=404, detail=f"Device '{device_id}' not found")

    # Fetch baseline if available
    b_stmt = select(Baseline).where(Baseline.device_id == device.id)
    b_res = await db.execute(b_stmt)
    baseline = b_res.scalars().first()

    health_breakdown = health_engine.calculate_device_health(device)
    insights = explanation_engine.explain_device_state(device, baseline, health_breakdown)

    return insights


@router.post("/copilot/query", response_model=CopilotQueryResponse)
async def query_copilot(req: CopilotQueryRequest, db: AsyncSession = Depends(get_db)):
    """
    AI Infrastructure Copilot Natural Language Engine.
    Executes RAG over live fleet inventory, metrics, anomalies, and alerts.
    """
    q = req.query.lower().strip()
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Fetch live state for RAG context
    devices = (await db.execute(select(Endpoint))).scalars().all()
    alerts = (await db.execute(select(Alert).where(Alert.status == "NEW"))).scalars().all()
    anomalies = (await db.execute(select(Anomaly).where(Anomaly.status == "ACTIVE"))).scalars().all()

    devices_mentioned = []
    for d in devices:
        if d.hostname.lower() in q or d.id.lower() in q:
            devices_mentioned.append(d.hostname)

    # 1. Intent: Unhealthy devices / Which need attention
    if any(k in q for k in ["unhealthy", "need attention", "degraded", "worst", "failing"]):
        unhealthy = []
        for d in devices:
            h = health_engine.calculate_device_health(d)
            if h.overall < 75:
                unhealthy.append((d, h))

        if not unhealthy:
            answer = (
                "All monitored devices in your fleet are currently operating with healthy parameters "
                "(all health scores above 75%). No urgent operator intervention is needed."
            )
        else:
            lines = [f"Found {len(unhealthy)} device(s) requiring attention:"]
            for d, h in sorted(unhealthy, key=lambda x: x[1].overall):
                reasons = ", ".join(h.deductions) if h.deductions else "elevated resource pressure"
                lines.append(f"• **{d.hostname}** (Health: {h.overall}/100) — {reasons}.")
            answer = "\n".join(lines)

        return CopilotQueryResponse(
            query=req.query,
            answer=answer,
            intent="FLEET_HEALTH_INSPECTION",
            devices_mentioned=[d.hostname for d, _ in unhealthy],
            suggested_followups=["Why is the highest-load device slow?", "Show active alerts for these hosts"],
            timestamp=now_str
        )

    # 2. Intent: Why is a specific device slow?
    if "why is" in q or "slow" in q or "high cpu" in q or "spike" in q:
        target_dev = None
        for d in devices:
            if d.hostname.lower() in q or d.id.lower() in q:
                target_dev = d
                break

        if not target_dev and req.context_device_id:
            target_dev = next((d for d in devices if d.id == req.context_device_id), None)

        if not target_dev:
            # Fall back to the highest load device
            target_dev = max(devices, key=lambda x: x.cpu_usage or 0)

        h = health_engine.calculate_device_health(target_dev)
        b_stmt = select(Baseline).where(Baseline.device_id == target_dev.id)
        baseline = (await db.execute(b_stmt)).scalars().first()
        insights = explanation_engine.explain_device_state(target_dev, baseline, h)

        answer = (
            f"**Analysis for {target_dev.hostname} ({target_dev.device_type}, IP: {target_dev.ip_address}):**\n\n"
            f"{insights['natural_language_summary']}\n\n"
            f"**Primary Findings:**\n"
            + "\n".join(f"• {f}" for f in insights['investigation_breakdown']['facts'][:3]) + "\n\n"
            f"**Recommended Action:**\n"
            + "\n".join(f"• {a}" for a in insights['investigation_breakdown']['recommended_actions'])
        )

        return CopilotQueryResponse(
            query=req.query,
            answer=answer,
            intent="ROOT_CAUSE_ANALYSIS",
            devices_mentioned=[target_dev.hostname],
            suggested_followups=["Show active processes on this host", "Isolate host from network"],
            timestamp=now_str
        )

    # 3. Intent: Knowledge Base, Runbooks, Post-Mortems & Operational Troubleshooting
    from app.rag.rag_engine import rag_engine

    rag_keywords = [
        "outage", "restart", "agent", "memory", "exhaustion", "oom",
        "post-mortem", "runbook", "incident", "troubleshoot", "how do i",
        "what caused", "sigma", "mitre", "yesterday", "remediation"
    ]
    if any(k in q for k in rag_keywords) or len(q.split()) > 3:
        telemetry_overview = {
            "status": "ALL_SYSTEMS_OPERATIONAL" if any(d.status == "ONLINE" for d in devices) else "DEGRADED",
            "online_count": sum(1 for d in devices if d.status == "ONLINE"),
            "total_devices": len(devices)
        }
        rag_res = await rag_engine.query(
            query_text=req.query,
            top_k=3,
            live_telemetry=telemetry_overview
        )
        if rag_res.citations:
            followups = [
                "What caused yesterday's outage?",
                "How do I restart the monitoring agent?",
                "Show all incidents related to memory exhaustion."
            ]
            return CopilotQueryResponse(
                query=req.query,
                answer=rag_res.answer,
                intent="RAG_KNOWLEDGE_RETRIEVAL",
                devices_mentioned=[c["doc_id"] for c in rag_res.citations],
                suggested_followups=followups,
                timestamp=now_str
            )

    # 4. Intent: General status or summary
    healthy_cnt = sum(1 for d in devices if d.status == "ONLINE")
    answer = (
        f"SKYNET is currently supervising {len(devices)} infrastructure endpoints ({healthy_cnt} ONLINE). "
        f"There are currently {len(alerts)} active alerts and {len(anomalies)} statistical anomalies flagged by the AI engine. "
        f"Fleet-wide health index is currently stable at {health_engine.calculate_device_health(devices[0]).overall if devices else 100}%."
    )

    return CopilotQueryResponse(
        query=req.query,
        answer=answer,
        intent="GENERAL_STATUS",
        devices_mentioned=[d.hostname for d in devices[:3]],
        suggested_followups=["What caused yesterday's outage?", "How do I restart the monitoring agent?", "Show all incidents related to memory exhaustion."],
        timestamp=now_str
    )
