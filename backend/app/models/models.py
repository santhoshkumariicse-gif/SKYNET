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

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(128), unique=True, nullable=False, index=True)
    slug = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    sites = relationship("Site", back_populates="organization", cascade="all, delete-orphan")

class Site(Base):
    __tablename__ = "sites"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(128), nullable=False) # Headquarters, Data Center, Branch Office A, Branch Office B
    code = Column(String(32), unique=True, nullable=False, index=True) # HQ-NYC, DC-FRA, BR-LON, BR-TYO
    location = Column(String(128), nullable=False) # "New York, USA", "Frankfurt, Germany"
    latitude = Column(Float, default=0.0)
    longitude = Column(Float, default=0.0)
    timezone = Column(String(64), default="UTC")
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    organization = relationship("Organization", back_populates="sites")
    device_groups = relationship("DeviceGroup", back_populates="site", cascade="all, delete-orphan")
    endpoints = relationship("Endpoint", back_populates="site")

class DeviceGroup(Base):
    __tablename__ = "device_groups"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    site_id = Column(String(36), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(128), nullable=False) # "Core Database Cluster", "Corporate Workstations"
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    site = relationship("Site", back_populates="device_groups")

class Endpoint(Base):
    __tablename__ = "endpoints"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    site_id = Column(String(36), ForeignKey("sites.id", ondelete="SET NULL"), nullable=True, index=True)
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
    tags = Column(JSON, default=list)
    last_seen = Column(DateTime(timezone=True), default=get_utc_now, index=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    site = relationship("Site", back_populates="endpoints")

# Device alias for Endpoint
Device = Endpoint

class Metric(Base):
    __tablename__ = "metrics"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    device_id = Column(String(64), ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    cpu = Column(Float, nullable=False, default=0.0)
    ram = Column(Float, nullable=False, default=0.0)
    gpu = Column(Float, nullable=False, default=0.0)
    disk = Column(Float, nullable=False, default=0.0)
    network = Column(Float, nullable=False, default=0.0)
    network_rx_mb = Column(Float, default=0.0)
    network_tx_mb = Column(Float, default=0.0)
    temperature_c = Column(Float, default=0.0)
    battery_pct = Column(Float, nullable=True)
    processes_count = Column(Integer, default=0)
    raw_vitals = Column(JSON, default=dict)
    timestamp = Column(DateTime(timezone=True), default=get_utc_now, index=True)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    device_id = Column(String(64), nullable=True, index=True)
    alert_type = Column(String(64), default="High CPU", index=True) # High CPU, High RAM, High GPU, Disk Critical, Device Offline
    severity = Column(String(32), nullable=False, default="Warning", index=True) # Info, Warning, Critical
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    source = Column(String(64), nullable=False, default="ANOMALY_ENGINE") # SIGMA_RULE, IOC_MATCH, ANOMALY_ENGINE
    status = Column(String(32), default="NEW", index=True) # NEW, ACKNOWLEDGED, SUPPRESSED, CLOSED
    acknowledged = Column(Boolean, default=False, index=True)
    host_name = Column(String(128), nullable=True, index=True)
    host_ip = Column(String(45), nullable=True)
    mitre_technique = Column(String(32), nullable=True) # e.g. T1059.001
    threat_score = Column(Integer, default=50)
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
    hmac_signature = Column(String(64), nullable=True, index=True)
    correlation_id = Column(String(64), nullable=True, index=True)
    workflow_id = Column(String(64), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    result = Column(String(32), default="SUCCESS")
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

class Baseline(Base):
    __tablename__ = "baselines"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    device_id = Column(String(36), ForeignKey("endpoints.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    avg_cpu = Column(Float, default=25.0)
    std_cpu = Column(Float, default=8.0)
    avg_ram = Column(Float, default=45.0)
    std_ram = Column(Float, default=6.0)
    avg_gpu = Column(Float, default=10.0)
    std_gpu = Column(Float, default=5.0)
    avg_disk = Column(Float, default=40.0)
    std_disk = Column(Float, default=2.0)
    avg_network = Column(Float, default=1.5)
    std_network = Column(Float, default=1.0)
    sample_count = Column(Integer, default=100)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    device_id = Column(String(36), ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    anomaly_type = Column(String(64), nullable=False, index=True) # CPU_SPIKE, MEMORY_LEAK, DISK_PRESSURE, NETWORK_SURGE, INACTIVITY
    anomaly_score = Column(Float, nullable=False, index=True) # 0 to 100
    confidence = Column(Float, nullable=False, default=0.90) # 0.0 to 1.0
    evidence = Column(JSON, default=dict)
    reason = Column(Text, nullable=False)
    status = Column(String(32), default="ACTIVE", index=True) # ACTIVE, INVESTIGATING, RESOLVED, FALSE_POSITIVE
    created_at = Column(DateTime(timezone=True), default=get_utc_now, index=True)

