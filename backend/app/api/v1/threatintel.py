from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.models import IOCRecord
from app.schemas.schemas import IOCLookupRequest, IOCLookupResponse
from app.services.threat_intel_service import threat_intel_service

router = APIRouter(prefix="/threatintel", tags=["Threat Intelligence"])

@router.post("/lookup", response_model=IOCLookupResponse)
async def lookup_indicator(req: IOCLookupRequest, db: AsyncSession = Depends(get_db)):
    res = await threat_intel_service.lookup_ioc(db, req.ioc_type, req.value)
    return res

@router.get("/iocs")
async def list_iocs(
    ioc_type: Optional[str] = Query(None),
    min_score: int = Query(0, ge=0, le=100),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(IOCRecord).where(IOCRecord.threat_score >= min_score).order_by(IOCRecord.last_seen.desc())
    if ioc_type:
        stmt = stmt.where(IOCRecord.ioc_type == ioc_type.upper())
    stmt = stmt.limit(limit)

    res = await db.execute(stmt)
    records = res.scalars().all()
    return records


from pydantic import BaseModel

class AddBlocklistRequest(BaseModel):
    ioc_value: str
    ioc_type: Optional[str] = "IP"
    reason: Optional[str] = "Manual perimeter blocklist addition"

@router.post("/blocklist")
async def add_to_blocklist(req: AddBlocklistRequest, db: AsyncSession = Depends(get_db)):
    """Adds an indicator directly to the firewall drop blocklist and logs to audit trail."""
    from app.models.models import AuditLog
    val = req.ioc_value.strip()

    stmt = select(IOCRecord).where(IOCRecord.ioc_value == val)
    res = await db.execute(stmt)
    record = res.scalars().first()

    if not record:
        record = IOCRecord(
            ioc_type=req.ioc_type.upper(),
            ioc_value=val,
            threat_score=100,
            malware_family="Firewall Blocklist",
            source="SOC Analyst",
            tags=["blocklist", "perimeter-drop"]
        )
        db.add(record)
    else:
        record.threat_score = 100
        record.tags = list(set((record.tags or []) + ["blocklist", "perimeter-drop"]))

    # Write Audit Log
    db.add(AuditLog(
        actor="admin (SOC LEAD)",
        action="IOC_BLOCKLIST_ADDED",
        resource_type="IOC",
        resource_id=val,
        payload={"reason": req.reason, "ioc_type": req.ioc_type},
        client_ip="127.0.0.1"
    ))

    await db.commit()
    await db.refresh(record)
    return {"status": "BLOCKED", "threat_score": 100, "message": f"Added {val} to perimeter blocklist", "record": record}

