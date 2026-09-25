import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def get_utc_now():
    return datetime.now(timezone.utc)

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Role(Base):
    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(64), unique=True, nullable=False, index=True) # e.g. ADMIN, L1_ANALYST, THREAT_HUNTER
    permissions = Column(JSON, nullable=False, default=list) # e.g. ['alerts:read', 'soar:execute']
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False)
    status = Column(String(32), default="ACTIVE") # ACTIVE, SUSPENDED, DEACTIVATED
    created_at = Column(DateTime(timezone=True), default=get_utc_now)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    role = relationship("Role", back_populates="users")
    assigned_incidents = relationship("Incident", back_populates="assignee")

class Endpoint(Base):
    __tablename__ = "endpoints"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    hostname = Column(String(128), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    os_name = Column(String(64), default="Windows")
    os_version = Column(String(64), default="11 Pro")
    device_type = Column(String(32), default="Workstation") # Workstation, Server, Laptop
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    disk_usage = Column(Float, default=0.0)
    network_rx_mb = Column(Float, default=0.0)
    network_tx_mb = Column(Float, default=0.0)
    status = Column(String(32), default="ONLINE", index=True) # ONLINE, OFFLINE, WARNING, COMPROMISED, ISOLATED
    agent_version = Column(String(32), default="1.0.0")
    last_seen = Column(DateTime(timezone=True), default=get_utc_now, index=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    severity = Column(String(16), nullable=False, index=True) # LOW, MEDIUM, HIGH, CRITICAL
    source = Column(String(64), nullable=False) # SIGMA_RULE, IOC_MATCH, BEHAVIORAL_ANOMALY
    status = Column(String(32), default="NEW", index=True) # NEW, ACKNOWLEDGED, SUPPRESSED, CLOSED
    host_name = Column(String(128), nullable=True, index=True)
    host_ip = Column(String(45), nullable=True)
    mitre_technique = Column(String(32), nullable=True) # e.g. T1059.001
    event_data = Column(JSON, default=dict)
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, index=True)

    incident = relationship("Incident", back_populates="alerts")

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_number = Column(String(32), unique=True, nullable=False, index=True) # e.g. INC-2026-0001
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(16), nullable=False, index=True) # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(32), default="NEW", index=True) # NEW, TRIAGED, INVESTIGATING, RESOLVED, CLOSED
    verdict = Column(String(64), default="UNCONFIRMED") # TRUE_POSITIVE, FALSE_POSITIVE, BENIGN
    assigned_to = Column(String(36), ForeignKey("users.id"), nullable=True)
    ai_summary = Column(Text, nullable=True)
    ai_root_cause = Column(Text, nullable=True)
    ai_recommended_action = Column(Text, nullable=True)
    mitre_tactics = Column(JSON, default=list)
    mitre_techniques = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, index=True)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    assignee = relationship("User", back_populates="assigned_incidents")
    alerts = relationship("Alert", back_populates="incident")
    evidence = relationship("Evidence", back_populates="incident", cascade="all, delete-orphan")

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=False, index=True)
    evidence_type = Column(String(64), nullable=False) # PROCESS_LOG, NETWORK_FLOW, FILE_HASH, IP_ADDRESS
    raw_payload = Column(JSON, nullable=False)
    hash_sha256 = Column(String(64), nullable=True, index=True)
    captured_at = Column(DateTime(timezone=True), default=get_utc_now)
    notes = Column(Text, nullable=True)

    incident = relationship("Incident", back_populates="evidence")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    actor = Column(String(128), nullable=False)
    action = Column(String(128), nullable=False, index=True) # LOGIN, CONTAIN_HOST, BLOCK_IP, STATUS_CHANGE
    resource_type = Column(String(64), nullable=False)
    resource_id = Column(String(128), nullable=False)
    payload = Column(JSON, default=dict)
    client_ip = Column(String(45), default="127.0.0.1")
    created_at = Column(DateTime(timezone=True), default=get_utc_now, index=True)

class IOCRecord(Base):
    __tablename__ = "ioc_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    ioc_type = Column(String(32), nullable=False, index=True) # IP, DOMAIN, SHA256, URL
    ioc_value = Column(String(255), unique=True, nullable=False, index=True)
    threat_score = Column(Integer, default=0) # 0 to 100
    malware_family = Column(String(128), nullable=True)
    source = Column(String(64), default="VIRUSTOTAL")
    tags = Column(JSON, default=list)
    first_seen = Column(DateTime(timezone=True), default=get_utc_now)
    last_seen = Column(DateTime(timezone=True), default=get_utc_now)

class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    action_type = Column(String(64), nullable=False, index=True) # ISOLATE_HOST, DISABLE_ACCOUNT, BLOCK_IP
    target = Column(String(128), nullable=False)
    target_ip = Column(String(64), nullable=True)
    incident_id = Column(String(36), nullable=True)
    risk_score = Column(Integer, default=90)
    reason = Column(Text, nullable=False)
    evidence = Column(Text, nullable=True)
    detection = Column(String(128), nullable=True)
    requested_by = Column(String(128), default="Autonomous SOAR Engine")
    status = Column(String(32), default="PENDING", index=True) # PENDING, APPROVED, DENIED
    exact_action = Column(Text, nullable=True)
    rollback_plan = Column(Text, nullable=True)
    approved_by = Column(String(128), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    signed_token = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, index=True)

class SavedHunt(Base):
    __tablename__ = "saved_hunts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(128), nullable=False, unique=True)
    query = Column(Text, nullable=False)
    mitre_technique = Column(String(32), nullable=True)
    author = Column(String(64), default="admin")
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

