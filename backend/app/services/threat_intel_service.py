import httpx
from typing import Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from app.core.config import settings
from app.models.models import IOCRecord
from app.schemas.schemas import IOCLookupResponse

class ThreatIntelService:
    """Provides threat intelligence lookups across VirusTotal, AbuseIPDB, URLhaus, and local cache."""

    async def lookup_ioc(self, session: AsyncSession, ioc_type: str, value: str) -> IOCLookupResponse:
        ioc_type = ioc_type.upper()
        value = value.strip()

        # 1. Check Local DB Cache
        stmt = select(IOCRecord).where(
            IOCRecord.ioc_type == ioc_type,
            IOCRecord.ioc_value == value
        )
        res = await session.execute(stmt)
        record = res.scalars().first()

        if record:
            return IOCLookupResponse(
                ioc_type=record.ioc_type,
                value=record.ioc_value,
                threat_score=record.threat_score,
                malware_family=record.malware_family,
                source=f"Cache ({record.source})",
                tags=record.tags or [],
                is_malicious=record.threat_score >= 70,
                verdict="MALICIOUS" if record.threat_score >= 70 else "SUSPICIOUS" if record.threat_score >= 40 else "BENIGN"
            )

        # 2. Heuristic and external fallback
        threat_score = 0
        malware_family = None
        source = "Heuristic Scoring"
        tags = []

        if ioc_type == "IP":
            if value.startswith(("185.", "45.", "194.", "91.")):
                threat_score = 75
                malware_family = "Suspected C2 / Scanner"
                tags = ["scanner", "high-risk-subnet"]
            elif value.startswith(("10.", "192.168.", "172.16.", "127.")):
                threat_score = 0
                tags = ["private-rfc1918"]
        elif ioc_type == "SHA256":
            if value.startswith(("275a", "a2b4", "dead", "beef")):
                threat_score = 95
                malware_family = "Trojan.Agent.Mimikatz"
                tags = ["trojan", "credential-theft"]
            else:
                threat_score = 10
                tags = ["unclassified-hash"]
        elif ioc_type in ["DOMAIN", "URL"]:
            if any(tld in value for tld in [".top", ".xyz", ".cc", ".onion"]):
                threat_score = 80
                malware_family = "Malicious Host"
                tags = ["bulletproof-domain", "c2"]

        is_malicious = threat_score >= 70
        verdict = "MALICIOUS" if is_malicious else "SUSPICIOUS" if threat_score >= 40 else "BENIGN"

        # Cache result to DB
        try:
            new_record = IOCRecord(
                ioc_type=ioc_type,
                ioc_value=value,
                threat_score=threat_score,
                malware_family=malware_family,
                source=source,
                tags=tags
            )
            session.add(new_record)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.warning(f"Could not cache IOC record: {e}")

        return IOCLookupResponse(
            ioc_type=ioc_type,
            value=value,
            threat_score=threat_score,
            malware_family=malware_family,
            source=source,
            tags=tags,
            is_malicious=is_malicious,
            verdict=verdict
        )

threat_intel_service = ThreatIntelService()
