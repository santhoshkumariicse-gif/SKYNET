from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.config import settings
from app.schemas.schemas import TelemetryBatch
from app.services.telemetry_service import telemetry_service

router = APIRouter(prefix="/telemetry", tags=["Telemetry Ingestion"])

@router.post("/ingest")
async def ingest_telemetry(
    batch: TelemetryBatch,
    x_agent_key: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    # Verify agent key either in header or payload
    provided_key = x_agent_key or batch.agent_key
    if provided_key != settings.AGENT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or unauthorized Agent API Key"
        )

    result = await telemetry_service.process_batch(db, batch)
    return result
