"""
SKYNET v5.0 — Immutable Audit Log API
Provides read access to the security audit trail for compliance and forensics.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.models import AuditLog

router = APIRouter(prefix="/audit", tags=["Audit Logs"])


@router.get("/logs")
async def get_audit_logs(
    action: Optional[str] = Query(None),
    actor: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    limit: int = Query(50, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve immutable audit trail entries."""
    stmt = select(AuditLog).order_by(AuditLog.created_at.desc())
    if action:
        stmt = stmt.where(AuditLog.action.ilike(f"%{action}%"))
    if actor:
        stmt = stmt.where(AuditLog.actor.ilike(f"%{actor}%"))
    if resource_type:
        stmt = stmt.where(AuditLog.resource_type == resource_type.upper())
    stmt = stmt.limit(limit)

    res = await db.execute(stmt)
    logs = res.scalars().all()

    return [
        {
            "id": log.id,
            "actor": log.actor,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "payload": log.payload,
            "client_ip": log.client_ip,
            "created_at": log.created_at.isoformat() if log.created_at else None
        }
        for log in logs
    ]
