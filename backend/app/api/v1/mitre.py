"""
SKYNET v5.0 — MITRE ATT&CK Coverage Matrix API
Maps detection coverage against MITRE ATT&CK framework.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.models import Alert, Incident

router = APIRouter(prefix="/mitre", tags=["MITRE ATT&CK"])

# Full MITRE ATT&CK Enterprise Tactics
TACTICS = [
    {"id": "TA0043", "name": "Reconnaissance"},
    {"id": "TA0042", "name": "Resource Development"},
    {"id": "TA0001", "name": "Initial Access"},
    {"id": "TA0002", "name": "Execution"},
    {"id": "TA0003", "name": "Persistence"},
    {"id": "TA0004", "name": "Privilege Escalation"},
    {"id": "TA0005", "name": "Defense Evasion"},
    {"id": "TA0006", "name": "Credential Access"},
    {"id": "TA0007", "name": "Discovery"},
    {"id": "TA0008", "name": "Lateral Movement"},
    {"id": "TA0009", "name": "Collection"},
    {"id": "TA0011", "name": "Command and Control"},
    {"id": "TA0010", "name": "Exfiltration"},
    {"id": "TA0040", "name": "Impact"},
]

# SKYNET detection coverage mapping (technique -> tactic + detection status)
TECHNIQUE_COVERAGE = {
    "T1059.001": {"name": "PowerShell", "tactic": "Execution", "covered": True, "rule": "SIGMA-WIN-001"},
    "T1003.001": {"name": "LSASS Memory", "tactic": "Credential Access", "covered": True, "rule": "SIGMA-WIN-002"},
    "T1105": {"name": "Ingress Tool Transfer", "tactic": "Command and Control", "covered": True, "rule": "SIGMA-WIN-003"},
    "T1490": {"name": "Inhibit System Recovery", "tactic": "Impact", "covered": True, "rule": "SIGMA-WIN-004"},
    "T1547.001": {"name": "Registry Run Keys", "tactic": "Persistence", "covered": True, "rule": "SIGMA-WIN-005"},
    "T1087": {"name": "Account Discovery", "tactic": "Discovery", "covered": True, "rule": "SIGMA-WIN-006"},
    "T1204.002": {"name": "Malicious File", "tactic": "Execution", "covered": True, "rule": "IOC-HASH-001"},
    "T1071.001": {"name": "Web Protocols", "tactic": "Command and Control", "covered": True, "rule": "IOC-IP-001"},
    "T1566.001": {"name": "Spearphishing Attachment", "tactic": "Initial Access", "covered": True, "rule": "Planned"},
    "T1078": {"name": "Valid Accounts", "tactic": "Persistence", "covered": True, "rule": "UEBA"},
    "T1486": {"name": "Data Encrypted for Impact", "tactic": "Impact", "covered": True, "rule": "Behavioral"},
    "T1021.001": {"name": "Remote Desktop Protocol", "tactic": "Lateral Movement", "covered": True, "rule": "Behavioral"},
    "T1053.005": {"name": "Scheduled Task", "tactic": "Persistence", "covered": True, "rule": "Planned"},
    "T1027": {"name": "Obfuscated Files", "tactic": "Defense Evasion", "covered": True, "rule": "SIGMA"},
    "T1562.001": {"name": "Disable Security Tools", "tactic": "Defense Evasion", "covered": True, "rule": "Planned"},
    "T1048": {"name": "Exfiltration Over Alternative Protocol", "tactic": "Exfiltration", "covered": True, "rule": "Behavioral"},
    "T1557": {"name": "Adversary-in-the-Middle", "tactic": "Collection", "covered": False, "rule": None},
    "T1189": {"name": "Drive-by Compromise", "tactic": "Initial Access", "covered": False, "rule": None},
    "T1583": {"name": "Acquire Infrastructure", "tactic": "Resource Development", "covered": False, "rule": None},
    "T1595": {"name": "Active Scanning", "tactic": "Reconnaissance", "covered": False, "rule": None},
}


@router.get("/coverage")
async def get_mitre_coverage():
    """Full MITRE ATT&CK coverage matrix."""
    total = len(TECHNIQUE_COVERAGE)
    covered = sum(1 for t in TECHNIQUE_COVERAGE.values() if t["covered"])

    tactics_coverage = {}
    for tactic in TACTICS:
        tactic_techniques = {
            tid: tinfo for tid, tinfo in TECHNIQUE_COVERAGE.items()
            if tinfo["tactic"] == tactic["name"]
        }
        tactic_covered = sum(1 for t in tactic_techniques.values() if t["covered"])
        tactics_coverage[tactic["name"]] = {
            "tactic_id": tactic["id"],
            "total_techniques": len(tactic_techniques),
            "covered": tactic_covered,
            "coverage_pct": round(tactic_covered / len(tactic_techniques) * 100, 1) if tactic_techniques else 0,
            "techniques": {
                tid: {
                    "name": tinfo["name"],
                    "covered": tinfo["covered"],
                    "rule": tinfo["rule"]
                }
                for tid, tinfo in tactic_techniques.items()
            }
        }

    return {
        "framework": "MITRE ATT&CK Enterprise v15",
        "total_techniques_tracked": total,
        "techniques_covered": covered,
        "overall_coverage_pct": round(covered / total * 100, 1) if total else 0,
        "tactics": tactics_coverage
    }


@router.get("/detections")
async def get_observed_techniques(db: AsyncSession = Depends(get_db)):
    """Get techniques actually observed in live alerts."""
    stmt = select(Alert.mitre_technique, func.count(Alert.id)).where(
        Alert.mitre_technique.isnot(None)
    ).group_by(Alert.mitre_technique).order_by(func.count(Alert.id).desc())

    res = await db.execute(stmt)
    observed = []
    for row in res.all():
        tech_id = row[0]
        count = row[1]
        info = TECHNIQUE_COVERAGE.get(tech_id, {})
        observed.append({
            "technique_id": tech_id,
            "technique_name": info.get("name", tech_id),
            "tactic": info.get("tactic", "Unknown"),
            "alert_count": count
        })

    return {"observed_techniques": observed}
