import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from loguru import logger
from app.schemas.schemas import TelemetryEvent

class DetectionMatch(BaseModel):
    rule_id: str
    rule_name: str
    severity: str # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    mitre_technique: str
    mitre_tactic: str
    matched_field: str
    matched_value: str

class SigmaRuleEngine:
    """Evaluates telemetry events against built-in Sigma & behavioral threat detection signatures."""

    def __init__(self):
        self.rules = [
            {
                "id": "SIGMA-WIN-001",
                "name": "Suspicious Encoded PowerShell Execution",
                "severity": "HIGH",
                "mitre_technique": "T1059.001",
                "mitre_tactic": "Execution",
                "description": "Detects execution of PowerShell with base64 encoded command arguments commonly used to bypass inspection.",
                "check": self._check_encoded_powershell
            },
            {
                "id": "SIGMA-WIN-002",
                "name": "LSASS Memory Dump Attempt (Credential Theft)",
                "severity": "CRITICAL",
                "mitre_technique": "T1003.001",
                "mitre_tactic": "Credential Access",
                "description": "Detects attempts to dump LSASS process memory to harvest plaintext credentials or NTLM hashes.",
                "check": self._check_lsass_dump
            },
            {
                "id": "SIGMA-WIN-003",
                "name": "Living-off-the-Land Binary Ingress Tool (Certutil/Bitsadmin)",
                "severity": "MEDIUM",
                "mitre_technique": "T1105",
                "mitre_tactic": "Ingress Tool Transfer",
                "description": "Detects native Windows administrative utilities being abused to download external payloads.",
                "check": self._check_lotl_download
            },
            {
                "id": "SIGMA-WIN-004",
                "name": "Volume Shadow Copy Deletion (Ransomware Preparation)",
                "severity": "CRITICAL",
                "mitre_technique": "T1490",
                "mitre_tactic": "Impact",
                "description": "Detects execution of commands that inhibit system recovery by destroying volume shadow backups.",
                "check": self._check_shadow_copy_deletion
            },
            {
                "id": "SIGMA-WIN-005",
                "name": "Suspicious Registry Run Key Modification (Persistence)",
                "severity": "HIGH",
                "mitre_technique": "T1547.001",
                "mitre_tactic": "Persistence",
                "description": "Detects modifications to Windows autostart registry keys to maintain persistence.",
                "check": self._check_registry_persistence
            },
            {
                "id": "SIGMA-WIN-006",
                "name": "Reconnaissance via Discovery Utilities",
                "severity": "LOW",
                "mitre_technique": "T1087",
                "mitre_tactic": "Discovery",
                "description": "Detects rapid enumeration of domain users, network shares, or active privileges.",
                "check": self._check_recon_commands
            },
            {
                "id": "SIGMA-WIN-007",
                "name": "Brute Force Authentication Burst (Event 4625)",
                "severity": "HIGH",
                "mitre_technique": "T1110.001",
                "mitre_tactic": "Credential Access",
                "description": "Detects multiple failed logon attempts indicating automated password spraying or brute-force.",
                "check": self._check_brute_force
            },
            {
                "id": "SIGMA-WIN-008",
                "name": "Internal Network Port Scanning Activity",
                "severity": "MEDIUM",
                "mitre_technique": "T1046",
                "mitre_tactic": "Discovery",
                "description": "Detects rapid scanning across multiple port ranges indicating internal reconnaissance.",
                "check": self._check_port_scan
            },
            {
                "id": "SIGMA-WIN-009",
                "name": "Suspicious Scheduled Task Persistence Creation",
                "severity": "HIGH",
                "mitre_technique": "T1053.005",
                "mitre_tactic": "Persistence",
                "description": "Detects creation of scheduled tasks designed to persist across system reboots.",
                "check": self._check_scheduled_task
            },
            {
                "id": "SIGMA-WIN-010",
                "name": "Antivirus Disablement & AMSI Bypass Attempt",
                "severity": "CRITICAL",
                "mitre_technique": "T1562.001",
                "mitre_tactic": "Defense Evasion",
                "description": "Detects tampering with Windows Defender, AMSI memory patches, or security agent termination.",
                "check": self._check_defense_tampering
            },
            {
                "id": "SIGMA-WIN-011",
                "name": "Ransomware Bulk File Encryption & Ransom Note",
                "severity": "CRITICAL",
                "mitre_technique": "T1486",
                "mitre_tactic": "Impact",
                "description": "Detects mass encryption artifacts, known ransomware extensions (.locked, .crypt), or ransom note generation.",
                "check": self._check_ransomware_activity
            },
            {
                "id": "SIGMA-WIN-012",
                "name": "Lateral Movement via Remote Command Execution (PsExec/WMI)",
                "severity": "HIGH",
                "mitre_technique": "T1021.002",
                "mitre_tactic": "Lateral Movement",
                "description": "Detects remote service execution or administrative share abuse across internal subnets.",
                "check": self._check_lateral_movement
            }
        ]

    def evaluate_event(self, event: TelemetryEvent) -> List[DetectionMatch]:
        matches: List[DetectionMatch] = []
        for rule in self.rules:
            try:
                match = rule["check"](event, rule)
                if match:
                    matches.append(match)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule['id']}: {e}")
        return matches

    def _check_encoded_powershell(self, event: TelemetryEvent, rule: Dict[str, Any]) -> Optional[DetectionMatch]:
        cmd = (event.process_command_line or "").lower()
        proc = (event.process_name or "").lower()
        if "powershell" in proc or "pwsh" in proc or "powershell" in cmd:
            if re.search(r"(-enc|-encodedcommand|-e\s+[a-za-z0-9+/=]{10,})", cmd, re.IGNORECASE):
                return DetectionMatch(
                    rule_id=rule["id"],
                    rule_name=rule["name"],
                    severity=rule["severity"],
                    description=rule["description"],
                    mitre_technique=rule["mitre_technique"],
                    mitre_tactic=rule["mitre_tactic"],
                    matched_field="process_command_line",
                    matched_value=event.process_command_line[:120] if event.process_command_line else ""
                )
        return None

    def _check_lsass_dump(self, event: TelemetryEvent, rule: Dict[str, Any]) -> Optional[DetectionMatch]:
        cmd = (event.process_command_line or "").lower()
        proc = (event.process_name or "").lower()
        if "mimikatz" in proc or "mimikatz" in cmd:
            return DetectionMatch(
                rule_id=rule["id"],
                rule_name=rule["name"],
                severity=rule["severity"],
                description=rule["description"],
                mitre_technique=rule["mitre_technique"],
                mitre_tactic=rule["mitre_tactic"],
                matched_field="process_name",
                matched_value=event.process_name or cmd
            )
        if "lsass" in cmd and ("procdump" in cmd or "comsvcs.dll" in cmd or "rundll32" in cmd or "minidump" in cmd):
            return DetectionMatch(
                rule_id=rule["id"],
                rule_name=rule["name"],
                severity=rule["severity"],
                description=rule["description"],
                mitre_technique=rule["mitre_technique"],
                mitre_tactic=rule["mitre_tactic"],
                matched_field="process_command_line",
                matched_value=event.process_command_line or ""
            )
        return None

    def _check_lotl_download(self, event: TelemetryEvent, rule: Dict[str, Any]) -> Optional[DetectionMatch]:
        cmd = (event.process_command_line or "").lower()
        if "certutil" in cmd and ("-urlcache" in cmd or "-split" in cmd):
            return DetectionMatch(
                rule_id=rule["id"],
                rule_name=rule["name"],
                severity=rule["severity"],
                description=rule["description"],
                mitre_technique=rule["mitre_technique"],
                mitre_tactic=rule["mitre_tactic"],
                matched_field="process_command_line",
                matched_value=event.process_command_line or ""
            )
        if "bitsadmin" in cmd and ("/transfer" in cmd or "/download" in cmd):
            return DetectionMatch(
                rule_id=rule["id"],
                rule_name=rule["name"],
                severity=rule["severity"],
                description=rule["description"],
                mitre_technique=rule["mitre_technique"],
                mitre_tactic=rule["mitre_tactic"],
                matched_field="process_command_line",
                matched_value=event.process_command_line or ""
            )
        return None

    def _check_shadow_copy_deletion(self, event: TelemetryEvent, rule: Dict[str, Any]) -> Optional[DetectionMatch]:
        cmd = (event.process_command_line or "").lower()
        if "vssadmin" in cmd and "delete" in cmd and "shadows" in cmd:
            return DetectionMatch(
                rule_id=rule["id"],
                rule_name=rule["name"],
                severity=rule["severity"],
                description=rule["description"],
                mitre_technique=rule["mitre_technique"],
                mitre_tactic=rule["mitre_tactic"],
                matched_field="process_command_line",
                matched_value=event.process_command_line or ""
            )
        if "wbadmin" in cmd and "delete" in cmd and "catalog" in cmd:
            return DetectionMatch(
                rule_id=rule["id"],
                rule_name=rule["name"],
                severity=rule["severity"],
                description=rule["description"],
                mitre_technique=rule["mitre_technique"],
                mitre_tactic=rule["mitre_tactic"],
                matched_field="process_command_line",
                matched_value=event.process_command_line or ""
            )
        return None

    def _check_registry_persistence(self, event: TelemetryEvent, rule: Dict[str, Any]) -> Optional[DetectionMatch]:
        cmd = (event.process_command_line or "").lower()
        if "reg" in cmd and "add" in cmd and ("currentversion\\run" in cmd or "currentversion\\runonce" in cmd):
            return DetectionMatch(
                rule_id=rule["id"],
                rule_name=rule["name"],
                severity=rule["severity"],
                description=rule["description"],
                mitre_technique=rule["mitre_technique"],
                mitre_tactic=rule["mitre_tactic"],
                matched_field="process_command_line",
                matched_value=event.process_command_line or ""
            )
        return None

    def _check_recon_commands(self, event: TelemetryEvent, rule: Dict[str, Any]) -> Optional[DetectionMatch]:
        cmd = (event.process_command_line or "").lower()
        if "whoami /all" in cmd or "whoami /priv" in cmd or "net user /domain" in cmd or "nltest /dclist" in cmd:
            return DetectionMatch(
                rule_id=rule["id"],
                rule_name=rule["name"],
                severity=rule["severity"],
                description=rule["description"],
                mitre_technique=rule["mitre_technique"],
                mitre_tactic=rule["mitre_tactic"],
                matched_field="process_command_line",
                matched_value=event.process_command_line or ""
            )
        return None

    def _check_brute_force(self, event: TelemetryEvent, rule: Dict[str, Any]) -> Optional[DetectionMatch]:
        # Event ID 4625 = Failed Logon in Windows Security
        if event.event_id_code == 4625 or (event.raw_payload and event.raw_payload.get("event_id") == 4625):
            fail_count = (event.raw_payload or {}).get("failure_count", 5)
            if fail_count >= 5:
                return DetectionMatch(
                    rule_id=rule["id"],
                    rule_name=rule["name"],
                    severity=rule["severity"],
                    description=rule["description"],
                    mitre_technique=rule["mitre_technique"],
                    mitre_tactic=rule["mitre_tactic"],
                    matched_field="event_id_code",
                    matched_value=f"Event 4625 (Failed Logon count: {fail_count}, Target: {event.user_name})"
                )
        return None

    def _check_port_scan(self, event: TelemetryEvent, rule: Dict[str, Any]) -> Optional[DetectionMatch]:
        cmd = (event.process_command_line or "").lower()
        proc = (event.process_name or "").lower()
        if "nmap" in proc or "nmap" in cmd or "masscan" in proc or "masscan" in cmd:
            return DetectionMatch(
                rule_id=rule["id"],
                rule_name=rule["name"],
                severity=rule["severity"],
                description=rule["description"],
                mitre_technique=rule["mitre_technique"],
                mitre_tactic=rule["mitre_tactic"],
                matched_field="process_command_line",
                matched_value=event.process_command_line or proc
            )
        # Port scan payload indicator
        if event.raw_payload and event.raw_payload.get("scanned_ports_count", 0) >= 20:
            return DetectionMatch(
                rule_id=rule["id"],
                rule_name=rule["name"],
                severity=rule["severity"],
                description=rule["description"],
                mitre_technique=rule["mitre_technique"],
                mitre_tactic=rule["mitre_tactic"],
                matched_field="raw_payload.scanned_ports_count",
                matched_value=f"{event.raw_payload.get('scanned_ports_count')} distinct destination ports in 10s"
            )
        return None

    def _check_scheduled_task(self, event: TelemetryEvent, rule: Dict[str, Any]) -> Optional[DetectionMatch]:
        cmd = (event.process_command_line or "").lower()
        if "schtasks" in cmd and ("/create" in cmd or "-create" in cmd):
            if "powershell" in cmd or "cmd.exe" in cmd or "regsvr32" in cmd or "mshta" in cmd or "/ru system" in cmd:
                return DetectionMatch(
                    rule_id=rule["id"],
                    rule_name=rule["name"],
                    severity=rule["severity"],
                    description=rule["description"],
                    mitre_technique=rule["mitre_technique"],
                    mitre_tactic=rule["mitre_tactic"],
                    matched_field="process_command_line",
                    matched_value=event.process_command_line or ""
                )
        return None

    def _check_defense_tampering(self, event: TelemetryEvent, rule: Dict[str, Any]) -> Optional[DetectionMatch]:
        cmd = (event.process_command_line or "").lower()
        if "set-mppreference" in cmd and ("-disablerealtimemonitoring" in cmd or "-disablebehaviormonitoring" in cmd or "-disableioavprotection" in cmd):
            return DetectionMatch(
                rule_id=rule["id"],
                rule_name=rule["name"],
                severity=rule["severity"],
                description=rule["description"],
                mitre_technique=rule["mitre_technique"],
                mitre_tactic=rule["mitre_tactic"],
                matched_field="process_command_line",
                matched_value=event.process_command_line or ""
            )
        if "amsiutils" in cmd and "amsiinitfailed" in cmd:
            return DetectionMatch(
                rule_id=rule["id"],
                rule_name=rule["name"],
                severity=rule["severity"],
                description=rule["description"],
                mitre_technique=rule["mitre_technique"],
                mitre_tactic=rule["mitre_tactic"],
                matched_field="process_command_line",
                matched_value=event.process_command_line or ""
            )
        return None

    def _check_ransomware_activity(self, event: TelemetryEvent, rule: Dict[str, Any]) -> Optional[DetectionMatch]:
        cmd = (event.process_command_line or "").lower()
        # Look for encryption command line or ransom note creation
        if any(keyword in cmd for keyword in [".locked", ".crypt", ".encrypted", "readme_for_decrypt", "how_to_recover_files", "ransom_note"]):
            return DetectionMatch(
                rule_id=rule["id"],
                rule_name=rule["name"],
                severity=rule["severity"],
                description=rule["description"],
                mitre_technique=rule["mitre_technique"],
                mitre_tactic=rule["mitre_tactic"],
                matched_field="process_command_line",
                matched_value=event.process_command_line or ""
            )
        return None

    def _check_lateral_movement(self, event: TelemetryEvent, rule: Dict[str, Any]) -> Optional[DetectionMatch]:
        cmd = (event.process_command_line or "").lower()
        proc = (event.process_name or "").lower()
        if "psexec" in proc or "psexec" in cmd or "paexec" in proc or "paexec" in cmd:
            return DetectionMatch(
                rule_id=rule["id"],
                rule_name=rule["name"],
                severity=rule["severity"],
                description=rule["description"],
                mitre_technique=rule["mitre_technique"],
                mitre_tactic=rule["mitre_tactic"],
                matched_field="process_command_line",
                matched_value=event.process_command_line or proc
            )
        if "wmic" in cmd and "/node:" in cmd and "process call create" in cmd:
            return DetectionMatch(
                rule_id=rule["id"],
                rule_name=rule["name"],
                severity=rule["severity"],
                description=rule["description"],
                mitre_technique=rule["mitre_technique"],
                mitre_tactic=rule["mitre_tactic"],
                matched_field="process_command_line",
                matched_value=event.process_command_line or ""
            )
        return None

sigma_engine = SigmaRuleEngine()
