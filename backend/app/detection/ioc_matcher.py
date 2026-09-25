from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import IOCRecord
from app.schemas.schemas import TelemetryEvent
from app.detection.sigma_engine import DetectionMatch

class IOCMatcher:
    """Matches telemetry indicators (IPs, hashes, domains) against known threat intelligence."""

    async def evaluate_event(self, session: AsyncSession, event: TelemetryEvent) -> List[DetectionMatch]:
        matches: List[DetectionMatch] = []

        # Check Process SHA256 Hash
        if event.process_hash_sha256:
            stmt = select(IOCRecord).where(
                IOCRecord.ioc_type == "SHA256",
                IOCRecord.ioc_value == event.process_hash_sha256.lower()
            )
            result = await session.execute(stmt)
            ioc = result.scalars().first()
            if ioc and ioc.threat_score >= 70:
                matches.append(DetectionMatch(
                    rule_id="IOC-HASH-001",
                    rule_name=f"Known Malicious File Hash ({ioc.malware_family or 'Trojan'})",
                    severity="CRITICAL" if ioc.threat_score >= 90 else "HIGH",
                    description=f"File hash {event.process_hash_sha256} matches known threat signature in intelligence database with threat score {ioc.threat_score}/100.",
                    mitre_technique="T1204.002",
                    mitre_tactic="Execution",
                    matched_field="process_hash_sha256",
                    matched_value=event.process_hash_sha256
                ))

        # Check Destination IP
        if event.dst_ip and event.dst_ip not in ["127.0.0.1", "0.0.0.0", "localhost"]:
            stmt = select(IOCRecord).where(
                IOCRecord.ioc_type == "IP",
                IOCRecord.ioc_value == event.dst_ip
            )
            result = await session.execute(stmt)
            ioc = result.scalars().first()
            if ioc and ioc.threat_score >= 70:
                matches.append(DetectionMatch(
                    rule_id="IOC-IP-001",
                    rule_name=f"C2 Communication to Malicious IP ({ioc.malware_family or 'C2 Server'})",
                    severity="CRITICAL" if ioc.threat_score >= 90 else "HIGH",
                    description=f"Outbound connection detected to high-risk malicious IP {event.dst_ip} flagged by {ioc.source} (Threat Score: {ioc.threat_score}/100).",
                    mitre_technique="T1071.001",
                    mitre_tactic="Command and Control",
                    matched_field="dst_ip",
                    matched_value=f"{event.dst_ip}:{event.dst_port or 0}"
                ))

        return matches

ioc_matcher = IOCMatcher()
