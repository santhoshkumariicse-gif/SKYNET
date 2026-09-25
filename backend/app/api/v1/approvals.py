"""
SKYNET v5.0 — Approvals API
Human-in-the-Loop Authorization Center for High-Impact Security Actions
(Endpoint Isolation, Account Revocation, Perimeter IP Blocking).
"""
import hmac
import hashlib
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.models import Approval, Endpoint, AuditLog, IOCRecord, User
from app.api.v1.auth import require_roles
from app.core.security import generate_audit_hmac
from app.services.telemetry_service import websocket_subscribers

router = APIRouter(prefix="/approvals", tags=["Human-in-the-Loop Approvals"])


def sign_approval_token(action_id: str, target: str) -> str:
    now_str = datetime.now(timezone.utc).isoformat()
    return generate_audit_hmac(
        actor="HUMAN_SOC_APPROVER",
        action="APPROVAL_TOKEN_SIGN",
        resource_type="APPROVAL",
        resource_id=f"{action_id}:{target}",
        timestamp_str=now_str
    )


@router.get("")
@router.get("/")
async def get_approvals(
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Approval).order_by(Approval.risk_score.desc(), Approval.created_at.desc())
    if status:
        stmt = stmt.where(Approval.status == status.upper())
    stmt = stmt.limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("/{approval_id}/approve")
async def approve_action(
    approval_id: str,
    current_user: User = Depends(require_roles("ADMIN", "INCIDENT_RESPONDER", "SOC_ANALYST")),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Approval).where(Approval.id == approval_id)
    res = await db.execute(stmt)
    approval = res.scalars().first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")

    if approval.status == "APPROVED":
        return approval

    now = datetime.now(timezone.utc)
    token = sign_approval_token(approval.id, approval.target)

    # Execute underlying containment
    if approval.action_type in ["ISOLATE_HOST", "SOAR_ISOLATE_HOST"]:
        # Find endpoint and isolate
        target_name = approval.target.split()[0]
        ep_res = await db.execute(select(Endpoint).where(
            (Endpoint.hostname == target_name) | (Endpoint.ip_address == target_name)
        ))
        ep = ep_res.scalars().first()
        if ep:
            ep.status = "ISOLATED"

    elif approval.action_type in ["BLOCK_IP", "BLOCK_IP_PERIMETER"]:
        target_ip = approval.target.split(":")[0].strip()
        ioc_res = await db.execute(select(IOCRecord).where(IOCRecord.ioc_value == target_ip))
        existing_ioc = ioc_res.scalars().first()
        if not existing_ioc:
            db.add(IOCRecord(
                ioc_type="IP",
                ioc_value=target_ip,
                threat_score=100,
                malware_family="Firewall Drop Rule",
                source="Analyst Approval",
                tags=["blocklist", "manual-approval"]
            ))

    # Update approval state
    approval.status = "APPROVED"
    approval.approved_by = current_user.username
    approval.approved_at = now
    approval.signed_token = token

    # Generate matching HMAC signature for the Audit Log row
    audit_sig = generate_audit_hmac(
        actor=current_user.username,
        action=f"APPROVAL_EXECUTED_{approval.action_type}",
        resource_type="CONTAINMENT",
        resource_id=approval.target
    )

    # Write Cryptographic Audit Log
    db.add(AuditLog(
        actor=current_user.username,
        action=f"APPROVAL_EXECUTED_{approval.action_type}",
        resource_type="CONTAINMENT",
        resource_id=approval.target,
        hmac_signature=audit_sig,
        workflow_id="WF-101",
        old_value="PENDING_APPROVAL",
        new_value="APPROVED_CONTAINED",
        result="SUCCESS",
        payload={
            "approval_id": approval.id,
            "action": approval.action_type,
            "signed_token": token,
            "reason": approval.reason,
            "exact_action": approval.exact_action,
            "rollback_plan": approval.rollback_plan,
        },
        client_ip="127.0.0.1"
    ))

    await db.commit()
    await db.refresh(approval)

    # Broadcast to WebSocket live stream
    for ws in websocket_subscribers:
        try:
            import asyncio
            asyncio.create_task(ws.send_json({
                "type": "CONTAINMENT_APPROVED",
                "target": approval.target,
                "action": approval.action_type,
                "token": token
            }))
        except Exception:
            pass

    return approval


@router.post("/{approval_id}/deny")
async def deny_action(approval_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Approval).where(Approval.id == approval_id)
    res = await db.execute(stmt)
    approval = res.scalars().first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")

    approval.status = "DENIED"

    # Write Audit Log
    db.add(AuditLog(
        actor="admin (SOC LEAD)",
        action=f"APPROVAL_DENIED_{approval.action_type}",
        resource_type="CONTAINMENT",
        resource_id=approval.target,
        payload={"approval_id": approval.id, "reason": approval.reason},
        client_ip="127.0.0.1"
    ))

    await db.commit()
    await db.refresh(approval)
    return approval
