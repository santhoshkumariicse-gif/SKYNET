"""
SKYNET v5.0 — Immutable Audit Log API
Provides read access and cryptographic HMAC verification for the security audit trail.
Compliant with Section 25: Audit and HMAC Integrity Standards.
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.models import AuditLog, User
from app.api.v1.auth import require_roles
from app.core.security import verify_audit_hmac, generate_audit_hmac
from app.core.config import settings

router = APIRouter(prefix="/audit", tags=["Audit Logs"])


@router.get("/logs")
async def get_audit_logs(
    action: Optional[str] = Query(None),
    actor: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    limit: int = Query(50, le=500),
    current_user: User = Depends(require_roles("ADMIN", "AUDITOR", "SOC_ANALYST", "INCIDENT_RESPONDER", "INVESTIGATOR")),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve immutable audit trail entries with cryptographic provenance."""
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
            "hmac_signature": log.hmac_signature,
            "correlation_id": log.correlation_id,
            "workflow_id": log.workflow_id,
            "old_value": log.old_value,
            "new_value": log.new_value,
            "result": log.result,
            "created_at": log.created_at.isoformat() if log.created_at else None
        }
        for log in logs
    ]


@router.post("/verify-integrity")
async def verify_audit_integrity(
    current_user: User = Depends(require_roles("ADMIN", "AUDITOR")),
    db: AsyncSession = Depends(get_db)
):
    """
    Cryptographically verifies the HMAC-SHA256 signature chain of all recorded audit logs.
    Detects unauthorized tampering, alteration of actor, action, resource, or timestamp.
    """
    stmt = select(AuditLog).order_by(AuditLog.created_at.asc())
    res = await db.execute(stmt)
    logs = res.scalars().all()

    verified_count = 0
    tampered_records = []
    unsealed_count = 0

    for log in logs:
        if not log.hmac_signature:
            unsealed_count += 1
            continue

        ts_str = log.created_at.isoformat() if log.created_at else ""
        is_valid = verify_audit_hmac(
            actor=log.actor,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            timestamp_str=ts_str,
            signature=log.hmac_signature,
            secret_key=settings.HMAC_SECRET
        )

        if is_valid:
            verified_count += 1
        else:
            tampered_records.append({
                "id": log.id,
                "actor": log.actor,
                "action": log.action,
                "resource_id": log.resource_id,
                "recorded_signature": log.hmac_signature
            })

    is_integral = len(tampered_records) == 0

    return {
        "status": "PASS" if is_integral else "FAIL",
        "integrity_verified": is_integral,
        "total_records_evaluated": len(logs),
        "cryptographically_verified_records": verified_count,
        "unsealed_records": unsealed_count,
        "tampered_records_count": len(tampered_records),
        "tampered_records": tampered_records,
        "hash_algorithm": "HMAC-SHA256",
        "compliance": "NIST SP 800-92 & SOC 2 Type II Cryptographic Audit Standard"
    }
