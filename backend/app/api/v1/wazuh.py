"""
SKYNET v5.0 — Wazuh XDR API Router
Provides endpoints for Wazuh cluster monitoring, agent fleet management,
webhook ingestion, vulnerability detection, and active response execution.
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.config import settings
from app.models.models import User
from app.services.wazuh_service import wazuh_service
from app.api.v1.auth import require_roles, get_current_user

router = APIRouter(prefix="/wazuh", tags=["Wazuh XDR Integration"])

class WazuhActiveResponseRequest(BaseModel):
    agent_id: str = Field(..., description="Target Wazuh agent ID (e.g. '001')")
    command: str = Field(..., description="Active response command: 'host-deny', 'firewall-drop', 'disable-account', 'restart-wazuh'")
    arguments: Optional[List[str]] = Field(default=[], description="Command arguments (e.g. ['-ip', '192.168.1.50'])")

class WazuhAlertWebhookPayload(BaseModel):
    timestamp: Optional[str] = None
    rule: Dict[str, Any]
    agent: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    full_log: Optional[str] = None

@router.get("/status")
async def get_wazuh_status():
    """Returns real-time operational status of Wazuh Manager, Indexer, and connected agents."""
    return await wazuh_service.get_cluster_status()

@router.get("/agents")
async def get_wazuh_agents(db: AsyncSession = Depends(get_db)):
    """Retrieves all registered and active Wazuh endpoint agents across the enterprise fleet."""
    agents = await wazuh_service.list_agents(db)
    return {"total": len(agents), "agents": agents}

@router.get("/vulnerabilities")
async def get_wazuh_vulnerabilities(agent_id: Optional[str] = None):
    """Retrieves vulnerability inventory discovered by Wazuh Vulnerability Detector module."""
    vulns = await wazuh_service.get_vulnerabilities(agent_id)
    return {"total": len(vulns), "vulnerabilities": vulns}

@router.post("/webhook")
async def receive_wazuh_webhook(
    alert_payload: Dict[str, Any],
    x_wazuh_secret: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Ingests live alert webhooks forwarded from Wazuh Manager.
    Normalizes the alert, routes to detection/correlation, and creates HMAC-sealed audit record.
    """
    # Verify webhook authentication if secret is configured
    if settings.WAZUH_WEBHOOK_SECRET and x_wazuh_secret:
        if x_wazuh_secret != settings.WAZUH_WEBHOOK_SECRET:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized Wazuh webhook token"
            )

    result = await wazuh_service.ingest_wazuh_alert(db, alert_payload)
    return result

@router.post("/active-response")
async def execute_wazuh_active_response(
    req: WazuhActiveResponseRequest,
    current_user: User = Depends(require_roles("ADMIN", "INCIDENT_RESPONDER", "SOC_ANALYST")),
    db: AsyncSession = Depends(get_db)
):
    """
    Executes an authorized active response containment action on a target Wazuh agent.
    Restricted to authorized SOC roles with cryptographic HMAC audit sealing.
    """
    result = await wazuh_service.trigger_active_response(
        session=db,
        agent_id=req.agent_id,
        command=req.command,
        arguments=req.arguments,
        actor=current_user.username
    )
    return result
