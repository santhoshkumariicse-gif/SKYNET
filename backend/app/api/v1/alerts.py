"""
SKYNET v5.0 — Alert Management & Triaging API
Endpoints for querying alerts, filtering by type/severity/device, and acknowledging alerts.
"""
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.models import Alert
from app.schemas.schemas import AlertOut, AlertCreate, AlertStatusUpdate

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=List[AlertOut])
async def get_alerts(
    severity: Optional[str] = Query(None, description="Info, Warning, Critical (or LOW, MEDIUM, HIGH, CRITICAL)"),
    status: Optional[str] = Query(None, description="NEW, ACKNOWLEDGED, SUPPRESSED, CLOSED"),
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    alert_type: Optional[str] = Query(None, description="High CPU, High RAM, High GPU, Disk Critical, Device Offline"),
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledgment state"),
    host: Optional[str] = Query(None, description="Filter by hostname"),
    limit: int = Query(50, le=500),
    db: AsyncSession = Depends(get_db)
):
    """List alerts with optional multi-dimensional filtering."""
    stmt = select(Alert).order_by(Alert.created_at.desc())

    if severity:
        stmt = stmt.where(Alert.severity.ilike(severity))
    if status:
        stmt = stmt.where(Alert.status == status.upper())
    if device_id:
        stmt = stmt.where(Alert.device_id == device_id)
    if alert_type:
        stmt = stmt.where(Alert.alert_type.ilike(f"%{alert_type}%"))
    if acknowledged is not None:
        stmt = stmt.where(Alert.acknowledged == acknowledged)
    if host:
        stmt = stmt.where(Alert.host_name.ilike(f"%{host}%"))

    stmt = stmt.limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/{alert_id}", response_model=AlertOut)
async def get_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve details for a single alert."""
    stmt = select(Alert).where(Alert.id == alert_id)
    res = await db.execute(stmt)
    alert = res.scalars().first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/{alert_id}/acknowledge", response_model=AlertOut)
async def acknowledge_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    """Acknowledge an alert, updating acknowledged=True and status=ACKNOWLEDGED."""
    stmt = select(Alert).where(Alert.id == alert_id)
    res = await db.execute(stmt)
    alert = res.scalars().first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.acknowledged = True
    alert.status = "ACKNOWLEDGED"
    await db.commit()
    await db.refresh(alert)
    return alert


@router.patch("/{alert_id}/status", response_model=AlertOut)
async def update_alert_status(alert_id: str, req: AlertStatusUpdate, db: AsyncSession = Depends(get_db)):
    """Update alert lifecycle status."""
    stmt = select(Alert).where(Alert.id == alert_id)
    res = await db.execute(stmt)
    alert = res.scalars().first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = req.status.upper()
    if req.status.upper() == "ACKNOWLEDGED":
        alert.acknowledged = True
    await db.commit()
    await db.refresh(alert)
    return alert
