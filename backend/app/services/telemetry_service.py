from typing import List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from app.models.models import Endpoint, Alert, AuditLog
from app.schemas.schemas import TelemetryBatch, TelemetryEvent
from app.detection.sigma_engine import sigma_engine
from app.detection.ioc_matcher import ioc_matcher
from app.services.correlation_service import correlation_service

# In-memory WebSocket broadcast subscribers
websocket_subscribers: List[Any] = []

async def broadcast_event(event_type: str, data: Dict[str, Any]):
    message = {"type": event_type, "timestamp": datetime.now(timezone.utc).isoformat(), "data": data}
    disconnected = []
    for ws in websocket_subscribers:
        try:
            await ws.send_json(message)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        if ws in websocket_subscribers:
            websocket_subscribers.remove(ws)

class TelemetryService:
    """Ingests, normalizes, detects threats, and correlates endpoint event streams."""

    async def process_batch(self, session: AsyncSession, batch: TelemetryBatch) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        alerts_created = []
        incidents_affected = []

        # 1. Register or Update Endpoint Health & Metrics
        stmt = select(Endpoint).where(Endpoint.hostname == batch.hostname)
        res = await session.execute(stmt)
        endpoint = res.scalars().first()

        if not endpoint:
            endpoint = Endpoint(
                hostname=batch.hostname,
                ip_address=batch.ip_address,
                os_name=batch.os_name,
                os_version=batch.os_version,
                device_type=batch.device_type,
                cpu_usage=batch.cpu_usage,
                memory_usage=batch.memory_usage,
                disk_usage=batch.disk_usage,
                network_rx_mb=batch.network_rx_mb,
                network_tx_mb=batch.network_tx_mb,
                status="ONLINE",
                agent_version=batch.agent_version,
                last_seen=now
            )
            session.add(endpoint)
        else:
            endpoint.ip_address = batch.ip_address
            endpoint.cpu_usage = batch.cpu_usage
            endpoint.memory_usage = batch.memory_usage
            endpoint.disk_usage = batch.disk_usage
            endpoint.network_rx_mb = batch.network_rx_mb
            endpoint.network_tx_mb = batch.network_tx_mb
            endpoint.last_seen = now
            if endpoint.status != "ISOLATED":
                endpoint.status = "ONLINE"

        await session.flush()

        # 2. Evaluate Each Telemetry Event
        for ev in batch.events:
            if not ev.host_name:
                ev.host_name = batch.hostname
            if not ev.host_ip:
                ev.host_ip = batch.ip_address

            # Sigma Rule Evaluation
            sigma_matches = sigma_engine.evaluate_event(ev)

            # Threat Intel IOC Evaluation
            ioc_matches = await ioc_matcher.evaluate_event(session, ev)

            all_matches = sigma_matches + ioc_matches

            # Create Alerts for matches
            for m in all_matches:
                new_alert = Alert(
                    title=m.rule_name,
                    description=m.description,
                    severity=m.severity,
                    source="SIGMA_RULE" if m.rule_id.startswith("SIGMA") else "IOC_MATCH",
                    status="NEW",
                    host_name=ev.host_name,
                    host_ip=ev.host_ip,
                    mitre_technique=m.mitre_technique,
                    event_data={
                        "rule_id": m.rule_id,
                        "mitre_tactic": m.mitre_tactic,
                        "matched_field": m.matched_field,
                        "matched_value": m.matched_value,
                        "process_name": ev.process_name,
                        "process_command_line": ev.process_command_line,
                        "process_hash_sha256": ev.process_hash_sha256,
                        "dst_ip": ev.dst_ip,
                        "dst_port": ev.dst_port,
                        "user_name": ev.user_name
                    }
                )
                session.add(new_alert)
                await session.flush()
                alerts_created.append(new_alert)

                # Flag endpoint as compromised if high/critical alert
                if m.severity in ["HIGH", "CRITICAL"] and endpoint.status != "ISOLATED":
                    endpoint.status = "COMPROMISED"

                # Trigger Correlation Engine
                incident = await correlation_service.correlate_alert(session, new_alert)
                if incident:
                    incidents_affected.append(incident.id)

                # Broadcast live alert via WebSocket
                await broadcast_event("ALERT_TRIGGERED", {
                    "alert_id": new_alert.id,
                    "title": new_alert.title,
                    "severity": new_alert.severity,
                    "host": new_alert.host_name,
                    "technique": new_alert.mitre_technique
                })

        await session.commit()

        # 3. Trigger Autonomous AI Investigation for any affected incidents
        from app.ai_agents.investigation_agent import investigation_agent
        for inc_id in set(incidents_affected):
            try:
                dossier = await investigation_agent.investigate_incident(session, inc_id)
                if dossier:
                    await broadcast_event("INCIDENT_INVESTIGATED", {
                        "incident_number": dossier.incident_number,
                        "recommended_severity": dossier.recommended_severity,
                        "confidence_score": dossier.confidence_score,
                        "summary": dossier.executive_summary
                    })
            except Exception as e:
                logger.error(f"Failed to run autonomous investigation for incident {inc_id}: {e}")

        # Broadcast endpoint telemetry update
        await broadcast_event("METRICS_UPDATED", {
            "hostname": endpoint.hostname,
            "status": endpoint.status,
            "cpu_usage": endpoint.cpu_usage,
            "memory_usage": endpoint.memory_usage,
            "disk_usage": endpoint.disk_usage
        })

        return {
            "status": "success",
            "events_processed": len(batch.events),
            "alerts_generated": len(alerts_created),
            "incidents_affected": len(set(incidents_affected))
        }

telemetry_service = TelemetryService()
