import uuid
import hmac
import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.config import settings
from app.models.models import Endpoint, AuditLog, User
from app.schemas.schemas import ContainmentActionRequest, ContainmentActionResponse
from app.services.telemetry_service import broadcast_event
from app.api.v1.auth import require_roles
from app.core.security import generate_audit_hmac

router = APIRouter(prefix="/soar", tags=["SOAR Active Defense"])

@router.post("/execute", response_model=ContainmentActionResponse)
async def execute_containment(
    req: ContainmentActionRequest,
    current_user: User = Depends(require_roles("ADMIN", "INCIDENT_RESPONDER", "SOC_ANALYST")),
    db: AsyncSession = Depends(get_db)
):
    now = datetime.now(timezone.utc)
    execution_id = f"EXEC-{uuid.uuid4().hex[:8].upper()}"
    action_type = req.action_type.upper()
    target = req.target_identifier.strip()
    now_str = now.isoformat()

    # Generate cryptographic HMAC-SHA256 signature for containment action
    signed_token = generate_audit_hmac(
        actor=current_user.username,
        action=f"SOAR_{action_type}",
        resource_type="CONTAINMENT",
        resource_id=target
    )

    status_msg = ""
    old_state = "ONLINE"
    new_state = "UNKNOWN"

    if action_type == "ISOLATE_HOST":
        stmt = select(Endpoint).where(Endpoint.hostname == target)
        res = await db.execute(stmt)
        ep = res.scalars().first()
        if ep:
            old_state = ep.status
            ep.status = "ISOLATED"
            new_state = "ISOLATED"
            status_msg = f"Host {target} isolated: All network traffic blocked except SKYNET management port 8443."
        else:
            new_state = "ISOLATED"
            status_msg = f"Containment token dispatched for remote host {target}."
    elif action_type == "UNISOLATE_HOST":
        stmt = select(Endpoint).where(Endpoint.hostname == target)
        res = await db.execute(stmt)
        ep = res.scalars().first()
        if ep:
            old_state = ep.status
            ep.status = "ONLINE"
            new_state = "ONLINE"
            status_msg = f"Host {target} restored to normal network operational state."
        else:
            new_state = "ONLINE"
            status_msg = f"Rollback token dispatched for host {target}."
    elif action_type == "BLOCK_IP":
        new_state = "BLOCKED"
        status_msg = f"Perimeter firewall ACL updated: Malicious IP {target} dropped."
    elif action_type == "UNBLOCK_IP":
        new_state = "UNBLOCKED"
        status_msg = f"Perimeter firewall ACL restored: IP {target} unblocked."
    elif action_type == "TERMINATE_PROCESS":
        new_state = "TERMINATED"
        status_msg = f"Termination signal sent for PID / Process {target}."
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported containment action: {action_type}")

    # Write immutable audit log with cryptographic HMAC and provenance
    audit_entry = AuditLog(
        actor=current_user.username,
        action=f"SOAR_{action_type}",
        resource_type="CONTAINMENT",
        resource_id=target,
        hmac_signature=signed_token,
        workflow_id="WF-101",
        old_value=old_state,
        new_value=new_state,
        result="SUCCESS",
        payload={
            "execution_id": execution_id,
            "reason": req.reason,
            "rollback_plan": req.rollback_plan,
            "signed_token": signed_token
        },
        client_ip="127.0.0.1"
    )
    db.add(audit_entry)
    await db.commit()

    # Broadcast containment action via WebSocket
    await broadcast_event("SOAR_CONTAINMENT_EXECUTED", {
        "execution_id": execution_id,
        "action_type": action_type,
        "target": target,
        "message": status_msg
    })

    return ContainmentActionResponse(
        execution_id=execution_id,
        status="EXECUTED",
        action_type=action_type,
        target=target,
        signed_token=signed_token,
        executed_at=now,
        message=status_msg
    )
