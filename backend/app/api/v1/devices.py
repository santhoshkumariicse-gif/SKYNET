"""
SKYNET v5.0 — Device Management & Registration API
Endpoints:
- POST /devices/register
- GET /devices
- GET /devices/{id}
"""
from datetime import datetime, timezone
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.config import settings
from app.models.models import Endpoint
from app.schemas.schemas import DeviceRegisterRequest, DeviceResponse

router = APIRouter(tags=["Devices"])


@router.post("/devices/register", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
@router.post("/register", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def register_device(
    payload: DeviceRegisterRequest,
    x_agent_key: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new infrastructure device or update an existing endpoint's registration.
    Validates agent authentication token.
    """
    if x_agent_key and x_agent_key != settings.AGENT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or unauthorized Agent API Key"
        )

    # Check if device already exists by ID or Hostname
    device_id = payload.id or f"DEV-{uuid.uuid4().hex[:12].upper()}"
    stmt = select(Endpoint).where(
        (Endpoint.id == device_id) | (Endpoint.hostname == payload.hostname)
    )
    res = await db.execute(stmt)
    device = res.scalars().first()

    now = datetime.now(timezone.utc)

    if device:
        # Update existing record
        device.hostname = payload.hostname
        device.ip_address = payload.ip_address
        device.os_name = payload.os_name
        device.os_version = payload.os_version
        device.device_type = payload.device_type
        device.agent_version = payload.agent_version
        device.status = "ONLINE"
        device.last_seen = now
    else:
        # Create new endpoint
        device = Endpoint(
            id=device_id,
            hostname=payload.hostname,
            ip_address=payload.ip_address,
            os_name=payload.os_name,
            os_version=payload.os_version,
            device_type=payload.device_type,
            status="ONLINE",
            agent_version=payload.agent_version,
            last_seen=now,
            created_at=now
        )
        db.add(device)

    await db.commit()
    await db.refresh(device)
    return device


@router.get("/devices", response_model=List[DeviceResponse])
async def list_devices(
    status: Optional[str] = Query(None, description="Filter by status: ONLINE, OFFLINE, COMPROMISED, ISOLATED"),
    device_type: Optional[str] = Query(None, description="Filter by device_type: Workstation, Server, Laptop, Android"),
    search: Optional[str] = Query(None, description="Search hostname or IP"),
    limit: int = Query(50, le=500),
    db: AsyncSession = Depends(get_db)
):
    """List all registered devices in the infrastructure inventory."""
    stmt = select(Endpoint).order_by(Endpoint.last_seen.desc())

    if status:
        stmt = stmt.where(Endpoint.status == status.upper())
    if device_type:
        stmt = stmt.where(Endpoint.device_type == device_type)
    if search:
        stmt = stmt.where(
            Endpoint.hostname.ilike(f"%{search}%") | Endpoint.ip_address.ilike(f"%{search}%")
        )

    stmt = stmt.limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/devices/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve details for a specific device by ID or Hostname."""
    stmt = select(Endpoint).where(
        (Endpoint.id == device_id) | (Endpoint.hostname == device_id)
    )
    res = await db.execute(stmt)
    device = res.scalars().first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device '{device_id}' not found in registry"
        )
    return device
