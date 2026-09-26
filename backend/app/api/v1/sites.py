"""
SKYNET v5.0 — Multi-Site Monitoring API
Endpoints:
- GET /sites
- GET /sites/{id}
- GET /sites/{id}/health
- GET /sites/comparison
- POST /sites
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.models import Site, Organization, DeviceGroup, Endpoint, Metric, Alert
from app.services.anomaly_service import health_engine
from app.services.risk_engine import risk_engine

router = APIRouter(prefix="/sites", tags=["Multi-Site Operations & Hierarchy"])


class SiteCreateRequest(BaseModel):
    name: str
    code: str
    location: str
    latitude: Optional[float] = 0.0
    longitude: Optional[float] = 0.0
    timezone: Optional[str] = "UTC"


@router.get("")
async def list_sites(db: AsyncSession = Depends(get_db)):
    """
    Returns all geographic sites with active device counts,
    site health scores, risk scores, and operational statuses.
    """
    sites_res = await db.execute(select(Site).order_by(Site.name.asc()))
    sites = sites_res.scalars().all()

    results = []
    for s in sites:
        # Count endpoints
        eps_res = await db.execute(select(Endpoint).where(Endpoint.site_id == s.id))
        endpoints = eps_res.scalars().all()

        total = len(endpoints)
        online = sum(1 for e in endpoints if e.status == "ONLINE")
        offline = sum(1 for e in endpoints if e.status == "OFFLINE")

        # Compute site health
        health_scores = []
        risk_scores = []
        for e in endpoints:
            h = health_engine.calculate_health_score(
                cpu=e.cpu_usage or 15.0,
                ram=e.memory_usage or 35.0,
                disk=e.disk_usage or 45.0,
                net=e.network_rx_mb or 10.0,
                status=e.status
            )
            health_scores.append(h["health_score"])

            r = risk_engine.calculate_device_risk(
                device_id=e.id,
                hostname=e.hostname,
                latest_metrics={"cpu_percent": e.cpu_usage, "memory_percent": e.memory_usage, "disk_percent": e.disk_usage},
                device_status=e.status
            )
            risk_scores.append(r.risk_score)

        avg_health = round(sum(health_scores) / len(health_scores)) if health_scores else 100
        avg_risk = round(sum(risk_scores) / len(risk_scores)) if risk_scores else 0

        # Fetch groups count
        grp_count_res = await db.execute(select(func.count(DeviceGroup.id)).where(DeviceGroup.site_id == s.id))
        grp_count = grp_count_res.scalar() or 0

        results.append({
            "id": s.id,
            "name": s.name,
            "code": s.code,
            "location": s.location,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "timezone": s.timezone,
            "device_count": total,
            "online_count": online,
            "offline_count": offline,
            "device_groups_count": grp_count,
            "health_score": avg_health,
            "risk_score": avg_risk,
            "status": "HEALTHY" if avg_health >= 80 and offline == 0 else ("DEGRADED" if avg_health >= 60 else "CRITICAL")
        })

    return results


@router.get("/comparison")
async def get_site_comparison(db: AsyncSession = Depends(get_db)):
    """
    Computes a comparative benchmarking matrix across all sites:
    Fleet distribution, Health differential, Average latency, Risk profile.
    """
    sites_res = await db.execute(select(Site))
    sites = sites_res.scalars().all()

    matrix = []
    for s in sites:
        eps_res = await db.execute(select(Endpoint).where(Endpoint.site_id == s.id))
        endpoints = eps_res.scalars().all()

        total = len(endpoints)
        online = sum(1 for e in endpoints if e.status == "ONLINE")
        cpu_avg = round(sum(e.cpu_usage or 0.0 for e in endpoints) / max(total, 1), 1)
        ram_avg = round(sum(e.memory_usage or 0.0 for e in endpoints) / max(total, 1), 1)

        health_scores = [
            health_engine.calculate_health_score(e.cpu_usage, e.memory_usage, e.disk_usage, status=e.status)["health_score"]
            for e in endpoints
        ]
        avg_health = round(sum(health_scores) / max(len(health_scores), 1)) if health_scores else 100

        matrix.append({
            "site_code": s.code,
            "site_name": s.name,
            "location": s.location,
            "device_count": total,
            "availability_pct": round((online / max(total, 1)) * 100.0, 1),
            "avg_cpu_percent": cpu_avg,
            "avg_memory_percent": ram_avg,
            "health_score": avg_health
        })

    return {
        "comparison_matrix": matrix,
        "highest_performing_site": max(matrix, key=lambda x: x["health_score"])["site_name"] if matrix else None,
        "highest_risk_site": min(matrix, key=lambda x: x["health_score"])["site_name"] if matrix else None
    }


@router.get("/{site_id}/health")
async def get_site_health(site_id: str, db: AsyncSession = Depends(get_db)):
    """
    Detailed telemetry and health analytics breakdown for a single site.
    """
    s_res = await db.execute(select(Site).where(Site.id == site_id))
    site = s_res.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found.")

    eps_res = await db.execute(select(Endpoint).where(Endpoint.site_id == site.id))
    endpoints = eps_res.scalars().all()

    devices_data = []
    for e in endpoints:
        h = health_engine.calculate_health_score(e.cpu_usage, e.memory_usage, e.disk_usage, status=e.status)
        devices_data.append({
            "id": e.id,
            "hostname": e.hostname,
            "ip_address": e.ip_address,
            "device_type": e.device_type,
            "status": e.status,
            "health_score": h["health_score"],
            "cpu_usage": e.cpu_usage,
            "memory_usage": e.memory_usage,
            "tags": e.tags
        })

    # Fetch groups
    grp_res = await db.execute(select(DeviceGroup).where(DeviceGroup.site_id == site.id))
    groups = [{"id": g.id, "name": g.name, "description": g.description} for g in grp_res.scalars().all()]

    return {
        "site": {
            "id": site.id,
            "name": site.name,
            "code": site.code,
            "location": site.location,
            "timezone": site.timezone
        },
        "device_count": len(devices_data),
        "device_groups": groups,
        "devices": devices_data
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_site(payload: SiteCreateRequest, db: AsyncSession = Depends(get_db)):
    """Registers a new regional site under the default organization."""
    org_res = await db.execute(select(Organization).limit(1))
    org = org_res.scalars().first()
    if not org:
        org = Organization(name="Default Org", slug="default-org")
        db.add(org)
        await db.flush()

    new_site = Site(
        organization_id=org.id,
        name=payload.name,
        code=payload.code.upper(),
        location=payload.location,
        latitude=payload.latitude,
        longitude=payload.longitude,
        timezone=payload.timezone
    )
    db.add(new_site)
    await db.commit()
    await db.refresh(new_site)
    return {"message": "Site created successfully.", "site_id": new_site.id, "code": new_site.code}
