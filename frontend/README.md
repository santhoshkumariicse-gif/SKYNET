# SKYNET v5.0 — Autonomous SOC Command Center Frontend

High-fidelity Next.js web application for the **SKYNET Autonomous Cyber Defense & Tier-1 SOC Analyst** platform.

---

## Architecture & Capabilities

- **SOC Command Center Dashboard (`/`)**: Real-time telemetry ingestion velocity, active threat incident spotlight, DEFCON elevated state monitoring, severity distributions, and 1-click active defense containment triggers.
- **Live Threat Alerts Triaging (`/alerts`)**: Multi-dimensional filtering by severity (Critical, High, Medium, Low), status (New, Acknowledged, Suppressed, Closed), and target host. Full raw telemetry payload JSON inspection and triage workflow controls.
- **Incident Cases & AI Dossier (`/incidents`)**: Multi-stage attack correlation cases with automated Tier-1 AI Analyst Executive Summaries, Root Cause Analysis, interactive Attack Causality Timelines, and Forensic Evidence Lockers.
- **Fleet & Asset Inventory (`/assets`)**: Real-time fleet health, OS distribution, resource utilization (CPU/Memory/Disk), and 1-click network containment (`ISOLATE_HOST` / `UNISOLATE_HOST`).
- **SOAR Active Defense Engine (`/soar`)**: Cryptographically signed response actions with HMAC-SHA256 tokens and immutable audit trail integration.
- **Threat Intelligence Platform (`/threatintel`)**: Multi-feed intelligence correlation (VirusTotal, AbuseIPDB, URLhaus), 0-100 threat score gauges, and cached indicators database.
- **MITRE ATT&CK® Enterprise Matrix (`/mitre`)**: Comprehensive detection coverage tracking across 14 enterprise tactics with live observed technique telemetry.
- **Forensic Audit Trail (`/audit`)**: Tamper-evident, chronological log of all security events and containment dispatches.

---

## Running Locally

```bash
# 1. Install dependencies
npm install

# 2. Run the development server
npm run dev

# App runs on http://localhost:3000
```
