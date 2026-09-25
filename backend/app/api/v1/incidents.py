from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.models import Incident, Alert, Evidence
from app.schemas.schemas import IncidentOut, IncidentCreate, IncidentUpdate
from app.ai_agents.investigation_agent import investigation_agent

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("", response_model=List[IncidentOut])
async def get_incidents(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Incident)
        .options(selectinload(Incident.evidence), selectinload(Incident.alerts))
        .order_by(Incident.created_at.desc())
    )
    if status:
        stmt = stmt.where(Incident.status == status.upper())
    if severity:
        stmt = stmt.where(Incident.severity == severity.upper())
    stmt = stmt.limit(limit)

    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/{incident_id}", response_model=IncidentOut)
async def get_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Incident)
        .options(selectinload(Incident.evidence), selectinload(Incident.alerts))
        .where(Incident.id == incident_id)
    )
    res = await db.execute(stmt)
    incident = res.scalars().first()
    if not incident:
        # Check by incident_number e.g. INC-2026-0001
        stmt2 = (
            select(Incident)
            .options(selectinload(Incident.evidence), selectinload(Incident.alerts))
            .where(Incident.incident_number == incident_id)
        )
        res2 = await db.execute(stmt2)
        incident = res2.scalars().first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.put("/{incident_id}", response_model=IncidentOut)
@router.patch("/{incident_id}", response_model=IncidentOut)
async def update_incident(incident_id: str, req: IncidentUpdate, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Incident)
        .options(selectinload(Incident.evidence), selectinload(Incident.alerts))
        .where(Incident.id == incident_id)
    )
    res = await db.execute(stmt)
    incident = res.scalars().first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if req.status:
        incident.status = req.status.upper()
    if req.verdict:
        incident.verdict = req.verdict.upper()
    if req.title:
        incident.title = req.title
    if req.description:
        incident.description = req.description
    if req.assigned_to:
        incident.assigned_to = req.assigned_to

    await db.commit()
    await db.refresh(incident)
    return incident

@router.post("/{incident_id}/investigate")
async def trigger_investigation(incident_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Incident).where(Incident.id == incident_id)
    res = await db.execute(stmt)
    incident = res.scalars().first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    dossier = await investigation_agent.investigate_incident(db, incident.id)
    if not dossier:
        raise HTTPException(status_code=500, detail="Investigation failed")
    return dossier
