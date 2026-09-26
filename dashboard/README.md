# SKYNET Real-Time SOC & Infrastructure Dashboard

Production-grade web console providing deep infrastructure visibility, time-series telemetry charts, alert triage, and SOAR containment controls.

---

## 1. Overview
The dashboard is built with Next.js, React, and Lucide Icons, providing:
- **Fleet Overview:** Real-time health matrix for Windows PCs, Laptops, Servers, and Android devices.
- **Hardware Telemetry:** Live gauges and time-series charts for CPU, RAM, Disk, GPU, and Network.
- **Security Command Center:** Unified incident queue, MITRE ATT&CK coverage, and live WebSocket feed.
- **SOAR Execution & HITL:** Containment action dispatch with cryptographically signed HMAC approval requests.

---

## 2. Directory Reference
The active dashboard application source code is maintained in [`frontend/`](../frontend/) for seamless Next.js workspace tooling.

### Running the Dashboard Locally:
```bash
cd frontend
npm install
npm run dev
```
Accessible at: `http://localhost:3000`
