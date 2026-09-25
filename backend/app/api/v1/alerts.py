from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.models import Alert
from app.schemas.schemas import AlertOut, AlertCreate, AlertStatusUpdate

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=List[AlertOut])
async def get_alerts(
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    host: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Alert).order_by(Alert.created_at.desc())
    if severity:
        stmt = stmt.where(Alert.severity == severity.upper())
    if status:
        stmt = stmt.where(Alert.status == status.upper())
    if host:
        stmt = stmt.where(Alert.host_name.ilike(f"%{host}%"))
    stmt = stmt.limit(limit)

    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/{alert_id}", response_model=AlertOut)
async def get_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Alert).where(Alert.id == alert_id)
    res = await db.execute(stmt)
    alert = res.scalars().first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.patch("/{alert_id}/status", response_model=AlertOut)
async def update_alert_status(alert_id: str, req: AlertStatusUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(Alert).where(Alert.id == alert_id)
    res = await db.execute(stmt)
    alert = res.scalars().first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = req.status.upper()
    await db.commit()
    await db.refresh(alert)
    return alert
