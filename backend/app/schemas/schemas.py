from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, EmailStr

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_minutes: int

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Telemetry & Endpoint Schemas ---
class TelemetryEvent(BaseModel):
    event_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    host_name: str
    host_ip: Optional[str] = None
    event_source: str = "sysmon" # sysmon, windows_security, syslog, host_monitor
    event_id_code: int = 1
    process_id: Optional[int] = None
    process_name: Optional[str] = None
    process_path: Optional[str] = None
    process_command_line: Optional[str] = None
    process_hash_sha256: Optional[str] = None
    parent_process_name: Optional[str] = None
    parent_process_command_line: Optional[str] = None
    user_name: Optional[str] = "SYSTEM"
    src_ip: Optional[str] = None
    src_port: Optional[int] = None
    dst_ip: Optional[str] = None
    dst_port: Optional[int] = None
    raw_payload: Optional[Dict[str, Any]] = None

class TelemetryBatch(BaseModel):
    agent_key: str
    hostname: str
    ip_address: str
    os_name: str = "Windows"
    os_version: str = "11 Pro"
    device_type: str = "Workstation"
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_rx_mb: float = 0.0
    network_tx_mb: float = 0.0
    agent_version: str = "1.0.0"
    events: List[TelemetryEvent] = []

class EndpointOut(BaseModel):
    id: str
    hostname: str
    ip_address: str
    os_name: str
    os_version: str
    device_type: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    status: str
    agent_version: str
    last_seen: datetime

    class Config:
        from_attributes = True

# --- Alert Schemas ---
class AlertCreate(BaseModel):
    title: str
    description: str
    severity: str = "MEDIUM" # LOW, MEDIUM, HIGH, CRITICAL
    source: str = "SIGMA_RULE"
    host_name: Optional[str] = None
    host_ip: Optional[str] = None
    mitre_technique: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = None

class AlertOut(BaseModel):
    id: str
    device_id: Optional[str] = None
    alert_type: Optional[str] = "High CPU"
    title: str
    description: str
    severity: str
    source: str
    status: str
    acknowledged: bool = False
    host_name: Optional[str] = None
    host_ip: Optional[str] = None
    mitre_technique: Optional[str] = None
    incident_id: Optional[str] = None
    created_at: datetime
    event_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class AlertStatusUpdate(BaseModel):
    status: str # NEW, ACKNOWLEDGED, SUPPRESSED, CLOSED

# --- Incident Schemas ---
class EvidenceOut(BaseModel):
    id: str
    evidence_type: str
    raw_payload: Dict[str, Any]
    hash_sha256: Optional[str] = None
    captured_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class IncidentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str = "HIGH"
    mitre_tactics: List[str] = []
    mitre_techniques: List[str] = []

class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None # NEW, TRIAGED, INVESTIGATING, RESOLVED, CLOSED
    verdict: Optional[str] = None # UNCONFIRMED, TRUE_POSITIVE, FALSE_POSITIVE
    assigned_to: Optional[str] = None

class IncidentOut(BaseModel):
    id: str
    incident_number: str
    title: str
    description: Optional[str] = None
    severity: str
    status: str
    verdict: str
    assigned_to: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_root_cause: Optional[str] = None
    ai_recommended_action: Optional[str] = None
    mitre_tactics: List[str] = []
    mitre_techniques: List[str] = []
    created_at: datetime
    updated_at: datetime
    evidence: List[EvidenceOut] = []
    alerts: List[AlertOut] = []

    class Config:
        from_attributes = True

# --- Threat Intelligence Schemas ---
class IOCLookupRequest(BaseModel):
    ioc_type: str # IP, DOMAIN, SHA256, URL
    value: str

class IOCLookupResponse(BaseModel):
    ioc_type: str
    value: str
    threat_score: int
    malware_family: Optional[str] = None
    source: str
    tags: List[str] = []
    is_malicious: bool
    verdict: str

# --- SOAR Containment Schemas ---
class ContainmentActionRequest(BaseModel):
    action_type: str # ISOLATE_HOST, UNISOLATE_HOST, BLOCK_IP, UNBLOCK_IP, TERMINATE_PROCESS
    target_identifier: str # Hostname, IP, or Process PID
    reason: str
    rollback_plan: Optional[str] = "Revert firewall block rule or restore network adapter state."

class ContainmentActionResponse(BaseModel):
    execution_id: str
    status: str # EXECUTED, PENDING_APPROVAL, FAILED
    action_type: str
    target: str
    signed_token: str
    executed_at: datetime
    message: str

# --- Investigation Dossier Schemas ---
class InvestigationDossier(BaseModel):
    incident_number: str
    confidence_score: float
    recommended_severity: str
    is_false_positive: bool
    executive_summary: str
    technical_root_cause: str
    attack_chain: List[str]
    mitre_mappings: List[str]
    suggested_actions: List[Dict[str, Any]]

# --- Phase-1 Core Device & Metrics Schemas ---
class DeviceRegisterRequest(BaseModel):
    id: Optional[str] = None
    hostname: str
    ip_address: str
    os_name: str = "Windows"
    os_version: str = "11 Pro"
    device_type: str = "Workstation"
    cpu_cores: Optional[int] = 4
    total_ram_mb: Optional[float] = 0.0
    total_disk_gb: Optional[float] = 0.0
    agent_version: str = "5.0.0"
    tags: Optional[List[str]] = Field(default_factory=list)

class DeviceResponse(BaseModel):
    id: str
    hostname: str
    ip_address: str
    os_name: str
    os_version: str
    device_type: str
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    status: str = "ONLINE"
    agent_version: str = "5.0.0"
    last_seen: datetime

    class Config:
        from_attributes = True

class MetricCreateRequest(BaseModel):
    device_id: str
    hostname: Optional[str] = None
    cpu: float = Field(..., ge=0.0, le=100.0)
    ram: float = Field(..., ge=0.0, le=100.0)
    gpu: Optional[float] = Field(default=0.0, ge=0.0, le=100.0)
    disk: float = Field(..., ge=0.0, le=100.0)
    network: Optional[float] = 0.0
    network_rx_mb: Optional[float] = 0.0
    network_tx_mb: Optional[float] = 0.0
    processes_count: Optional[int] = 0
    battery_pct: Optional[float] = None
    timestamp: Optional[datetime] = None
    raw_vitals: Optional[Dict[str, Any]] = Field(default_factory=dict)

class MetricResponse(BaseModel):
    id: str
    device_id: str
    cpu: float
    ram: float
    gpu: float
    disk: float
    network: float
    timestamp: datetime

    class Config:
        from_attributes = True
