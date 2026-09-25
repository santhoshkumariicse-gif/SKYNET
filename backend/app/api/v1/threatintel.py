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
