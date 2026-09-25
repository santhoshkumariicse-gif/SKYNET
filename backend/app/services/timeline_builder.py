from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Alert, Evidence, Incident

class TimelineBuilder:
    """Constructs microsecond-ordered forensic attack timelines from evidence and alerts."""

    async def build_incident_timeline(self, session: AsyncSession, incident_id: str) -> List[Dict[str, Any]]:
        timeline: List[Dict[str, Any]] = []

        # 1. Fetch Correlated Alerts
        stmt_alerts = select(Alert).where(Alert.incident_id == incident_id).order_by(Alert.created_at.asc())
        alerts_res = await session.execute(stmt_alerts)
        alerts = alerts_res.scalars().all()

        for a in alerts:
            timeline.append({
                "id": a.id,
                "timestamp": a.created_at.isoformat() if a.created_at else None,
                "event_type": "ALERT",
                "title": a.title,
                "description": a.description,
                "severity": a.severity,
                "host_name": a.host_name,
                "mitre_technique": a.mitre_technique,
                "details": a.event_data
            })

        # 2. Fetch Attached Evidence Items
        stmt_evidence = select(Evidence).where(Evidence.incident_id == incident_id).order_by(Evidence.captured_at.asc())
        ev_res = await session.execute(stmt_evidence)
        ev_items = ev_res.scalars().all()

        for ev in ev_items:
            timeline.append({
                "id": ev.id,
                "timestamp": ev.captured_at.isoformat() if ev.captured_at else None,
                "event_type": "EVIDENCE",
                "title": f"Forensic Artifact: {ev.evidence_type}",
                "description": ev.notes or f"Captured {ev.evidence_type} payload",
                "severity": "INFO",
                "host_name": ev.raw_payload.get("host_name") if isinstance(ev.raw_payload, dict) else None,
                "mitre_technique": None,
                "details": ev.raw_payload
            })

        # Sort combined events chronologically
        timeline.sort(key=lambda x: x["timestamp"] or "")
        return timeline

timeline_builder = TimelineBuilder()
