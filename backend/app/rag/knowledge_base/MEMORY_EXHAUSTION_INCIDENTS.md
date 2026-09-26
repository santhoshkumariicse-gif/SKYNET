# SKYNET INCIDENT CATALOG: Fleet Memory Exhaustion & OOM Events
**Document ID:** KB-INCIDENTS-MEM-003  
**Category:** Incident Records & Runbooks  
**Tags:** memory, exhaustion, oom, leak, dev-build-runner, incident, runbook  
**Last Updated:** 2026-09-25  

## Summary of Memory Exhaustion Incidents
Across the SKYNET fleet, a total of 3 incidents have been recorded regarding physical memory saturation and out-of-memory (OOM) conditions.

### Incident 1: INC-2026-0019 — DEV-BUILD-RUNNER Worker Heap Leak
- **Date:** 2026-09-24 08:30 UTC
- **Impacted Host:** DEV-BUILD-RUNNER (IP: 10.0.1.88)
- **Severity:** HIGH
- **Symptoms:** RAM usage steadily escalated from 45% to 94.8% over a 6-hour build cycle. Node.js runner processes failed to release v8 heap allocations during parallel test artifact compilation.
- **Root Cause:** Memory leak in custom build matrix test runner caching large mock payload buffers in module-level global variables.
- **Remediation:** Configured `--max-old-space-size=4096` and automated nightly restart cron for runner worker daemon. Autonomous SOAR rule `AUTO_RESTART_LEAKING_WORKER` provisioned.

### Incident 2: INC-2026-0031 — Docker Daemon Cgroup Memory Pressure on CI Cluster
- **Date:** 2026-09-23 14:15 UTC
- **Impacted Host:** K8S-WORKER-04 (IP: 10.0.2.14)
- **Severity:** MEDIUM
- **Symptoms:** Kernel invoked OOM killer, terminating secondary monitoring telemetry forwarder. Host RAM reached 98.2%.
- **Root Cause:** Multiple concurrent Docker builds exceeded host physical memory boundaries without individual container memory cgroup limits.
- **Remediation:** Enforced container memory limits (`mem_limit: 2g`) in all compose configs and Kubernetes pod specs.

### Incident 3: INC-2026-0038 — TEST-RIG-01 Synthetic Stress Spill
- **Date:** 2026-09-22 19:40 UTC
- **Impacted Host:** TEST-RIG-01 (IP: 192.168.10.15)
- **Severity:** HIGH
- **Symptoms:** Synthetic stress generator exceeded baseline thresholds, consuming 15.2GB of 16GB available RAM.
- **Root Cause:** Controlled performance testing load script ran without cleanup trap on process SIGINT.
- **Remediation:** Added automatic process watchdog and timeout threshold to test harness.

## General Memory Troubleshooting & Recovery Steps
1. Identify high-consumption processes:
   ```powershell
   Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 10 Name, Id, @{Name="RAM (MB)";Expression={[math]::round($_.WorkingSet64/1MB,2)}}
   ```
2. Trigger automated memory compaction or recycle target process via SOAR playbook `/soar/playbooks/memory_recycle`.
3. If swap space is saturated, verify paging file configuration and clear non-essential system caches.
