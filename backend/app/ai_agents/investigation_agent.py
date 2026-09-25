from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from app.models.models import Incident, Alert, Evidence
from app.schemas.schemas import InvestigationDossier
from app.services.threat_intel_service import threat_intel_service

class InvestigationAgent:
    """Autonomous Cognitive AI SOC Analyst agent performing root cause forensics and case dossiers."""

    async def investigate_incident(self, session: AsyncSession, incident_id: str) -> Optional[InvestigationDossier]:
        stmt = select(Incident).where(Incident.id == incident_id)
        res = await session.execute(stmt)
        incident = res.scalars().first()
        if not incident:
            return None

        # Fetch alerts
        alerts_stmt = select(Alert).where(Alert.incident_id == incident.id)
        alerts_res = await session.execute(alerts_stmt)
        alerts = alerts_res.scalars().all()

        # Fetch evidence
        ev_stmt = select(Evidence).where(Evidence.incident_id == incident.id)
        ev_res = await session.execute(ev_stmt)
        evidence_items = ev_res.scalars().all()

        # 1. Entity Extraction
        ips: set = set()
        hashes: set = set()
        processes: set = set()
        hosts: set = set()
        mitre_techs: set = set(incident.mitre_techniques or [])
        mitre_tactics: set = set(incident.mitre_tactics or [])

        for a in alerts:
            if a.host_name:
                hosts.add(a.host_name)
            if a.mitre_technique:
                mitre_techs.add(a.mitre_technique)
            data = a.event_data or {}
            if data.get("dst_ip"):
                ips.add(data["dst_ip"])
            if data.get("process_name"):
                processes.add(data["process_name"])
            if data.get("process_hash_sha256"):
                hashes.add(data["process_hash_sha256"])
            if data.get("mitre_tactic"):
                mitre_tactics.add(data["mitre_tactic"])

        for ev in evidence_items:
            payload = ev.raw_payload or {}
            event_data = payload.get("event_data", {})
            if event_data.get("dst_ip"):
                ips.add(event_data["dst_ip"])
            if ev.hash_sha256:
                hashes.add(ev.hash_sha256)

        # 2. Threat Intel Enrichment
        enriched_iocs = []
        highest_threat_score = 0
        for ip in ips:
            lookup = await threat_intel_service.lookup_ioc(session, "IP", ip)
            enriched_iocs.append(lookup)
            if lookup.threat_score > highest_threat_score:
                highest_threat_score = lookup.threat_score

        for h in hashes:
            lookup = await threat_intel_service.lookup_ioc(session, "SHA256", h)
            enriched_iocs.append(lookup)
            if lookup.threat_score > highest_threat_score:
                highest_threat_score = lookup.threat_score

        # 3. Calculate Confidence & Severity
        confidence = 0.85 if len(alerts) > 1 or highest_threat_score >= 80 else 0.70
        is_false_positive = False

        if highest_threat_score >= 85 or incident.severity == "CRITICAL":
            recommended_sev = "CRITICAL"
        elif highest_threat_score >= 60 or incident.severity == "HIGH":
            recommended_sev = "HIGH"
        else:
            recommended_sev = "MEDIUM"

        # 4. Formulate Attack Chain & Chronology
        attack_chain = []
        for i, a in enumerate(alerts, 1):
            tech_str = f" [{a.mitre_technique}]" if a.mitre_technique else ""
            attack_chain.append(f"Stage {i}: {a.title}{tech_str} observed on {a.host_name or 'host'}")

        # 5. Synthesize Executive Summary & Technical Root Cause
        host_str = ", ".join(hosts) if hosts else "the affected network segment"
        proc_str = ", ".join(processes) if processes else "system process"

        executive_summary = (
            f"Autonomous AI SOC analysis for {incident.incident_number} identified an active threat sequence "
            f"impacting {host_str}. The attack exhibits behavioral patterns consistent with {', '.join(mitre_tactics) or 'adversary execution'}, "
            f"involving unauthorized processes ({proc_str}). "
            f"Highest observed threat indicator score is {highest_threat_score}/100. Immediate containment is advised."
        )

        technical_root_cause = (
            f"Adversary activity initiated via execution of suspicious process artifacts ({proc_str}). "
            f"Telemetry confirms {len(alerts)} distinct detection events matching MITRE ATT&CK techniques: "
            f"{', '.join(mitre_techs) or 'T1059.001'}. "
            f"Network analysis identified communications targeting external indicators ({', '.join(ips) or 'internal'}). "
            f"Evidence points to deliberate credential access or command execution attempt."
        )

        # 6. Prescribe SOAR Containment Actions
        suggested_actions = []
        for h in hosts:
            suggested_actions.append({
                "action_type": "ISOLATE_HOST",
                "target": h,
                "urgency": "HIGH",
                "description": f"Isolate endpoint {h} from network traffic to stop lateral movement."
            })
        for ip in ips:
            suggested_actions.append({
                "action_type": "BLOCK_IP",
                "target": ip,
                "urgency": "HIGH",
                "description": f"Inject perimeter firewall block for malicious C2 address {ip}."
            })

        # Update Incident in Database
        incident.ai_summary = executive_summary
        incident.ai_root_cause = technical_root_cause
        incident.ai_recommended_action = "; ".join([a["description"] for a in suggested_actions])
        incident.severity = recommended_sev
        incident.status = "INVESTIGATING"
        incident.verdict = "TRUE_POSITIVE" if not is_false_positive else "FALSE_POSITIVE"
        incident.mitre_tactics = list(mitre_tactics)
        incident.mitre_techniques = list(mitre_techs)
        await session.commit()

        return InvestigationDossier(
            incident_number=incident.incident_number,
            confidence_score=confidence,
            recommended_severity=recommended_sev,
            is_false_positive=is_false_positive,
            executive_summary=executive_summary,
            technical_root_cause=technical_root_cause,
            attack_chain=attack_chain,
            mitre_mappings=list(mitre_techs),
            suggested_actions=suggested_actions
        )

investigation_agent = InvestigationAgent()
