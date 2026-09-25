from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.timeline_builder import timeline_builder
from app.ai_agents.investigation_agent import investigation_agent
from app.schemas.schemas import InvestigationDossier

router = APIRouter(prefix="/investigation", tags=["Investigation"])

@router.get("/{incident_id}/timeline")
async def get_incident_timeline(incident_id: str, db: AsyncSession = Depends(get_db)):
    timeline = await timeline_builder.build_incident_timeline(db, incident_id)
    return {"incident_id": incident_id, "event_count": len(timeline), "timeline": timeline}

@router.get("/{incident_id}/dossier", response_model=InvestigationDossier)
async def get_investigation_dossier(incident_id: str, db: AsyncSession = Depends(get_db)):
    dossier = await investigation_agent.investigate_incident(db, incident_id)
    if not dossier:
        raise HTTPException(status_code=404, detail="Incident not found or investigation failed")
    return dossier
