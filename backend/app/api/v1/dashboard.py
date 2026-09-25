"""
SKYNET v5.0 — SOC Command Center Dashboard API
Provides aggregated statistics for the main dashboard view.
"""
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.models import Alert, Incident, Endpoint, IOCRecord, AuditLog, Evidence

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Returns comprehensive SOC command center statistics."""
    now = datetime.now(timezone.utc)
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)

    # --- Alert Statistics ---
    total_alerts = (await db.execute(select(func.count(Alert.id)))).scalar() or 0
    alerts_24h = (await db.execute(
        select(func.count(Alert.id)).where(Alert.created_at >= last_24h)
    )).scalar() or 0
    critical_alerts = (await db.execute(
        select(func.count(Alert.id)).where(Alert.severity == "CRITICAL")
    )).scalar() or 0
    high_alerts = (await db.execute(
        select(func.count(Alert.id)).where(Alert.severity == "HIGH")
    )).scalar() or 0
    new_alerts = (await db.execute(
        select(func.count(Alert.id)).where(Alert.status == "NEW")
    )).scalar() or 0

    # Alert severity breakdown
    alert_by_severity = {}
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        count = (await db.execute(
            select(func.count(Alert.id)).where(Alert.severity == sev)
        )).scalar() or 0
        alert_by_severity[sev] = count

    # Alert source breakdown
    alert_by_source = {}
    for src in ["SIGMA_RULE", "IOC_MATCH", "BEHAVIORAL_ANOMALY"]:
        count = (await db.execute(
            select(func.count(Alert.id)).where(Alert.source == src)
        )).scalar() or 0
        alert_by_source[src] = count

    # --- Incident Statistics ---
    total_incidents = (await db.execute(select(func.count(Incident.id)))).scalar() or 0
    open_incidents = (await db.execute(
        select(func.count(Incident.id)).where(
            Incident.status.in_(["NEW", "TRIAGED", "INVESTIGATING"])
        )
    )).scalar() or 0
    critical_incidents = (await db.execute(
        select(func.count(Incident.id)).where(Incident.severity == "CRITICAL")
    )).scalar() or 0

    incident_by_status = {}
    for status in ["NEW", "TRIAGED", "INVESTIGATING", "RESOLVED", "CLOSED"]:
        count = (await db.execute(
            select(func.count(Incident.id)).where(Incident.status == status)
        )).scalar() or 0
        incident_by_status[status] = count

    incident_by_severity = {}
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        count = (await db.execute(
            select(func.count(Incident.id)).where(Incident.severity == sev)
        )).scalar() or 0
        incident_by_severity[sev] = count

    # --- Endpoint Statistics ---
    total_endpoints = (await db.execute(select(func.count(Endpoint.id)))).scalar() or 0
    online_endpoints = (await db.execute(
        select(func.count(Endpoint.id)).where(Endpoint.status == "ONLINE")
    )).scalar() or 0
    compromised_endpoints = (await db.execute(
        select(func.count(Endpoint.id)).where(Endpoint.status == "COMPROMISED")
    )).scalar() or 0
    isolated_endpoints = (await db.execute(
        select(func.count(Endpoint.id)).where(Endpoint.status == "ISOLATED")
    )).scalar() or 0

    endpoint_by_status = {}
    for st in ["ONLINE", "OFFLINE", "WARNING", "COMPROMISED", "ISOLATED"]:
        count = (await db.execute(
            select(func.count(Endpoint.id)).where(Endpoint.status == st)
        )).scalar() or 0
        endpoint_by_status[st] = count

    # --- Threat Intelligence Statistics ---
    total_iocs = (await db.execute(select(func.count(IOCRecord.id)))).scalar() or 0
    malicious_iocs = (await db.execute(
        select(func.count(IOCRecord.id)).where(IOCRecord.threat_score >= 70)
    )).scalar() or 0

    # --- SOAR Actions ---
    total_actions = (await db.execute(
        select(func.count(AuditLog.id)).where(AuditLog.action.like("SOAR_%"))
    )).scalar() or 0

    # --- Mean Time to Respond (simulated) ---
    mttr_minutes = 4.2 if total_incidents > 0 else 0

    return {
        "timestamp": now.isoformat(),
        "alerts": {
            "total": total_alerts,
            "last_24h": alerts_24h,
            "critical": critical_alerts,
            "high": high_alerts,
            "new": new_alerts,
            "by_severity": alert_by_severity,
            "by_source": alert_by_source
        },
        "incidents": {
            "total": total_incidents,
            "open": open_incidents,
            "critical": critical_incidents,
            "by_status": incident_by_status,
            "by_severity": incident_by_severity
        },
        "endpoints": {
            "total": total_endpoints,
            "online": online_endpoints,
            "compromised": compromised_endpoints,
            "isolated": isolated_endpoints,
            "by_status": endpoint_by_status
        },
        "threat_intelligence": {
            "total_iocs": total_iocs,
            "malicious": malicious_iocs
        },
        "soar": {
            "total_actions": total_actions
        },
        "performance": {
            "mttr_minutes": mttr_minutes,
            "automation_rate": "90%",
            "detection_coverage": "85%"
        }
    }


@router.get("/recent-activity")
async def get_recent_activity(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Returns a feed of recent alerts, incidents, and SOAR actions."""
    activities = []

    # Recent Alerts
    alerts_stmt = select(Alert).order_by(Alert.created_at.desc()).limit(limit)
    alerts_res = await db.execute(alerts_stmt)
    for a in alerts_res.scalars().all():
        activities.append({
            "id": a.id,
            "type": "ALERT",
            "title": a.title,
            "severity": a.severity,
            "status": a.status,
            "host": a.host_name,
            "timestamp": a.created_at.isoformat() if a.created_at else None
        })

    # Recent Incidents
    incidents_stmt = select(Incident).order_by(Incident.created_at.desc()).limit(limit)
    incidents_res = await db.execute(incidents_stmt)
    for inc in incidents_res.scalars().all():
        activities.append({
            "id": inc.id,
            "type": "INCIDENT",
            "title": inc.title,
            "severity": inc.severity,
            "status": inc.status,
            "host": None,
            "timestamp": inc.created_at.isoformat() if inc.created_at else None
        })

    # Recent SOAR Actions
    soar_stmt = select(AuditLog).where(
        AuditLog.action.like("SOAR_%")
    ).order_by(AuditLog.created_at.desc()).limit(limit)
    soar_res = await db.execute(soar_stmt)
    for log in soar_res.scalars().all():
        activities.append({
            "id": log.id,
            "type": "SOAR_ACTION",
            "title": f"{log.action}: {log.resource_id}",
            "severity": "INFO",
            "status": "EXECUTED",
            "host": log.resource_id,
            "timestamp": log.created_at.isoformat() if log.created_at else None
        })

    # Sort by timestamp descending
    activities.sort(key=lambda x: x["timestamp"] or "", reverse=True)
    return activities[:limit]
