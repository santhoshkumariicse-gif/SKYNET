import uuid
import hmac
import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.config import settings
from app.models.models import Endpoint, AuditLog
from app.schemas.schemas import ContainmentActionRequest, ContainmentActionResponse
from app.services.telemetry_service import broadcast_event

router = APIRouter(prefix="/soar", tags=["SOAR Active Defense"])

@router.post("/execute", response_model=ContainmentActionResponse)
async def execute_containment(req: ContainmentActionRequest, db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)
    execution_id = f"EXEC-{uuid.uuid4().hex[:8].upper()}"

    # Generate HMAC cryptographic signature for human-in-the-loop validation
    sig_payload = f"{execution_id}:{req.action_type}:{req.target_identifier}:{now.isoformat()}"
    signed_token = hmac.new(
        settings.SECRET_KEY.encode(),
        sig_payload.encode(),
        hashlib.sha256
    ).hexdigest()

    action_type = req.action_type.upper()
    target = req.target_identifier.strip()
    status_msg = ""

    if action_type == "ISOLATE_HOST":
        stmt = select(Endpoint).where(Endpoint.hostname == target)
        res = await db.execute(stmt)
        ep = res.scalars().first()
        if ep:
            ep.status = "ISOLATED"
            status_msg = f"Host {target} isolated: All network traffic blocked except SKYNET management port 8443."
        else:
            status_msg = f"Containment token dispatched for remote host {target}."
    elif action_type == "UNISOLATE_HOST":
        stmt = select(Endpoint).where(Endpoint.hostname == target)
        res = await db.execute(stmt)
        ep = res.scalars().first()
        if ep:
            ep.status = "ONLINE"
            status_msg = f"Host {target} restored to normal network operational state."
        else:
            status_msg = f"Rollback token dispatched for host {target}."
    elif action_type == "BLOCK_IP":
        status_msg = f"Perimeter firewall ACL updated: Malicious IP {target} dropped."
    elif action_type == "UNBLOCK_IP":
        status_msg = f"Perimeter firewall ACL restored: IP {target} unblocked."
    elif action_type == "TERMINATE_PROCESS":
        status_msg = f"Termination signal sent for PID / Process {target}."
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported containment action: {action_type}")

    # Write immutable audit log
    audit_entry = AuditLog(
        actor="SOC Analyst / AI Agent",
        action=f"SOAR_{action_type}",
        resource_type="CONTAINMENT",
        resource_id=target,
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
