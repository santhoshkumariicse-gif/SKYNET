# SKYNET DETECTION CATALOG: Sigma Rules & Threat Correlation Matrix
**Document ID:** KB-DETECTION-SIGMA-004  
**Category:** Detection Engineering & Rules  
**Tags:** sigma, detection, correlation, mitre, wazuh, rules  
**Last Updated:** 2026-09-25  

## Overview
SKYNET correlates endpoint hardware telemetry, process execution logs, and network connection events against a repository of Sigma rules mapped to the MITRE ATT&CK enterprise matrix.

## Active Rules
1. **Rule 90011: Suspicious PowerShell Obfuscation & Download Cradle**
   - **MITRE Technique:** T1059.001 (PowerShell Execution), T1105 (Ingress Tool Transfer)
   - **Pattern:** `powershell.exe` with `-NoP`, `-Enc`, `-ExecutionPolicy Bypass`, or `DownloadString` web requests.
   - **Severity:** HIGH
   - **Auto-Action:** Create incident dossier, alert SOC team, isolate endpoint if risk score > 90.

2. **Rule 90012: LSASS Memory Dumping via Procdump / Comsvcs.dll**
   - **MITRE Technique:** T1003.001 (OS Credential Dumping: LSASS Memory)
   - **Pattern:** Execution of `procdump.exe -ma lsass.exe` or `rundll32.exe comsvcs.dll, MiniDump`.
   - **Severity:** CRITICAL
   - **Auto-Action:** Immediately freeze offending process, revoke active user session tokens, flag Defcon 2 alert.

3. **Rule 90015: Shadow Copy Deletion (Ransomware Preparation)**
   - **MITRE Technique:** T1490 (Inhibit System Recovery)
   - **Pattern:** `vssadmin.exe delete shadows /all /quiet` or `wmic shadowcopy delete`.
   - **Severity:** CRITICAL
   - **Auto-Action:** Execute autonomous network quarantine, take emergency filesystem snapshot.
