import random
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from app.models.models import Alert, Incident, Evidence

class CorrelationService:
    """Correlates alerts across hosts and time to cluster related threat indicators into Incidents."""

    async def correlate_alert(self, session: AsyncSession, alert: Alert) -> Optional[Incident]:
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(hours=1)

        # 1. Look for an open Incident on the same host within the last hour
        if alert.host_name:
            stmt = select(Incident).join(Alert, Alert.incident_id == Incident.id).where(
                Alert.host_name == alert.host_name,
                Incident.status.in_(["NEW", "TRIAGED", "INVESTIGATING"]),
                Incident.created_at >= window_start
            ).order_by(Incident.created_at.desc())
            res = await session.execute(stmt)
            existing_incident = res.scalars().first()

            if existing_incident:
                logger.info(f"Correlating alert '{alert.title}' to existing incident {existing_incident.incident_number}")
                alert.incident_id = existing_incident.id
                # Elevate incident severity if new alert is higher
                if alert.severity == "CRITICAL":
                    existing_incident.severity = "CRITICAL"
                elif alert.severity == "HIGH" and existing_incident.severity in ["LOW", "MEDIUM"]:
                    existing_incident.severity = "HIGH"
                if alert.mitre_technique and alert.mitre_technique not in (existing_incident.mitre_techniques or []):
                    techs = list(existing_incident.mitre_techniques or [])
                    techs.append(alert.mitre_technique)
                    existing_incident.mitre_techniques = techs

                # Create evidence record
                evidence = Evidence(
                    incident_id=existing_incident.id,
                    evidence_type="CORRELATED_ALERT",
                    raw_payload={
                        "alert_id": alert.id,
                        "title": alert.title,
                        "source": alert.source,
                        "event_data": alert.event_data
                    },
                    hash_sha256=(alert.event_data or {}).get("process_hash_sha256"),
                    notes=f"Auto-correlated alert: {alert.title}"
                )
                session.add(evidence)
                await session.commit()
                return existing_incident

        # 2. If the alert is HIGH or CRITICAL, automatically raise a new Incident
        if alert.severity in ["HIGH", "CRITICAL"]:
            count_res = await session.execute(select(func.count(Incident.id)))
            next_num = (count_res.scalar() or 0) + 1
            inc_number = f"INC-2026-{next_num:04d}"

            logger.info(f"Escalating {alert.severity} alert '{alert.title}' to new incident: {inc_number}")
            new_incident = Incident(
                incident_number=inc_number,
                title=f"{alert.title} on {alert.host_name or 'Network'}",
                description=alert.description,
                severity=alert.severity,
                status="NEW",
                verdict="UNCONFIRMED",
                mitre_techniques=[alert.mitre_technique] if alert.mitre_technique else [],
                mitre_tactics=[alert.event_data.get("mitre_tactic")] if alert.event_data and "mitre_tactic" in alert.event_data else ["Execution"]
            )
            session.add(new_incident)
            await session.flush() # assign ID

            alert.incident_id = new_incident.id

            # Create initial evidence item
            evidence = Evidence(
                incident_id=new_incident.id,
                evidence_type="TRIGGERING_ALERT",
                raw_payload={
                    "alert_id": alert.id,
                    "title": alert.title,
                    "source": alert.source,
                    "event_data": alert.event_data
                },
                hash_sha256=(alert.event_data or {}).get("process_hash_sha256"),
                notes=f"Root triggering alert: {alert.title}"
            )
            session.add(evidence)
            await session.commit()
            return new_incident

        return None

correlation_service = CorrelationService()
