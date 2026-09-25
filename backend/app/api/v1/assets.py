"""
SKYNET v5.0 — Endpoint & Asset Management API
Provides CRUD for managed endpoints/assets with health telemetry.
"""
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.models import Endpoint, Alert, AuditLog
from app.schemas.schemas import EndpointOut
from app.services.telemetry_service import broadcast_event

router = APIRouter(prefix="/assets", tags=["Assets & Endpoints"])


@router.get("", response_model=List[EndpointOut])
async def list_endpoints(
    status: Optional[str] = Query(None),
    device_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db)
):
    """List all managed endpoints with optional filtering."""
    stmt = select(Endpoint).order_by(Endpoint.last_seen.desc())
    if status:
        stmt = stmt.where(Endpoint.status == status.upper())
    if device_type:
        stmt = stmt.where(Endpoint.device_type == device_type)
    if search:
        stmt = stmt.where(
            Endpoint.hostname.ilike(f"%{search}%") |
            Endpoint.ip_address.ilike(f"%{search}%")
        )
    stmt = stmt.limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/stats")
async def get_asset_stats(db: AsyncSession = Depends(get_db)):
    """Aggregated asset health statistics."""
    total = (await db.execute(select(func.count(Endpoint.id)))).scalar() or 0

    by_status = {}
    for st in ["ONLINE", "OFFLINE", "WARNING", "COMPROMISED", "ISOLATED"]:
        count = (await db.execute(
            select(func.count(Endpoint.id)).where(Endpoint.status == st)
        )).scalar() or 0
        by_status[st] = count

    by_type = {}
    for dt in ["Workstation", "Server", "Laptop"]:
        count = (await db.execute(
            select(func.count(Endpoint.id)).where(Endpoint.device_type == dt)
        )).scalar() or 0
        by_type[dt] = count

    by_os = {}
    os_res = await db.execute(
        select(Endpoint.os_name, func.count(Endpoint.id)).group_by(Endpoint.os_name)
    )
    for row in os_res.all():
        by_os[row[0]] = row[1]

    # Average resource utilization
    avg_cpu = (await db.execute(select(func.avg(Endpoint.cpu_usage)))).scalar() or 0
    avg_mem = (await db.execute(select(func.avg(Endpoint.memory_usage)))).scalar() or 0
    avg_disk = (await db.execute(select(func.avg(Endpoint.disk_usage)))).scalar() or 0

    return {
        "total": total,
        "by_status": by_status,
        "by_type": by_type,
        "by_os": by_os,
        "avg_utilization": {
            "cpu": round(avg_cpu, 1),
            "memory": round(avg_mem, 1),
            "disk": round(avg_disk, 1)
        }
    }


@router.get("/{endpoint_id}", response_model=EndpointOut)
async def get_endpoint(endpoint_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific endpoint by ID or hostname."""
    stmt = select(Endpoint).where(Endpoint.id == endpoint_id)
    res = await db.execute(stmt)
    endpoint = res.scalars().first()
    if not endpoint:
        # Try by hostname
        stmt2 = select(Endpoint).where(Endpoint.hostname == endpoint_id)
        res2 = await db.execute(stmt2)
        endpoint = res2.scalars().first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return endpoint


@router.get("/{endpoint_id}/alerts")
async def get_endpoint_alerts(
    endpoint_id: str,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Get all alerts for a specific endpoint."""
    # Resolve hostname
    stmt = select(Endpoint).where(
        (Endpoint.id == endpoint_id) | (Endpoint.hostname == endpoint_id)
    )
    res = await db.execute(stmt)
    endpoint = res.scalars().first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    alerts_stmt = select(Alert).where(
        Alert.host_name == endpoint.hostname
    ).order_by(Alert.created_at.desc()).limit(limit)
    alerts_res = await db.execute(alerts_stmt)
    alerts = alerts_res.scalars().all()

    return {
        "endpoint": endpoint.hostname,
        "total_alerts": len(alerts),
        "alerts": [
            {
                "id": a.id,
                "title": a.title,
                "severity": a.severity,
                "status": a.status,
                "source": a.source,
                "mitre_technique": a.mitre_technique,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in alerts
        ]
    }


@router.post("/{endpoint_id}/isolate")
async def isolate_endpoint(endpoint_id: str, db: AsyncSession = Depends(get_db)):
    """Network-isolate an endpoint for containment."""
    stmt = select(Endpoint).where(
        (Endpoint.id == endpoint_id) | (Endpoint.hostname == endpoint_id)
    )
    res = await db.execute(stmt)
    endpoint = res.scalars().first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    endpoint.status = "ISOLATED"
    audit = AuditLog(
        actor="SOC Analyst",
        action="ISOLATE_HOST",
        resource_type="ENDPOINT",
        resource_id=endpoint.hostname,
        payload={"previous_status": endpoint.status, "ip": endpoint.ip_address}
    )
    db.add(audit)
    await db.commit()

    await broadcast_event("ENDPOINT_ISOLATED", {
        "hostname": endpoint.hostname,
        "ip": endpoint.ip_address
    })

    return {"status": "success", "message": f"Endpoint {endpoint.hostname} isolated"}


@router.post("/{endpoint_id}/unisolate")
async def unisolate_endpoint(endpoint_id: str, db: AsyncSession = Depends(get_db)):
    """Restore network access to an isolated endpoint."""
    stmt = select(Endpoint).where(
        (Endpoint.id == endpoint_id) | (Endpoint.hostname == endpoint_id)
    )
    res = await db.execute(stmt)
    endpoint = res.scalars().first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    endpoint.status = "ONLINE"
    audit = AuditLog(
        actor="SOC Analyst",
        action="UNISOLATE_HOST",
        resource_type="ENDPOINT",
        resource_id=endpoint.hostname,
        payload={"ip": endpoint.ip_address}
    )
    db.add(audit)
    await db.commit()

    await broadcast_event("ENDPOINT_RESTORED", {
        "hostname": endpoint.hostname,
        "ip": endpoint.ip_address
    })

    return {"status": "success", "message": f"Endpoint {endpoint.hostname} restored to ONLINE"}
