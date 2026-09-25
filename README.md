# SKYNET: Version 5.0 – Autonomous SOC & XDR Enterprise Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Next.js: 14](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Supported-2496ED)](https://www.docker.com/)

SKYNET v5.0 is an enterprise-grade Autonomous Security Operations Center (SOC) and Extended Detection and Response (XDR) platform. Designed for hyperscale enterprise environments and Managed Security Service Providers (MSSPs), SKYNET delivers sub-second automated threat detection, multi-agent AI investigation, zero-trust response orchestration (SOAR), and global threat intelligence sharing.

---

## 🌟 Key Architecture & Capabilities

- **Unified Telemetry Fabric**: High-throughput distributed ingestion handling Syslog, Windows Event Logs, CloudTrail, NetFlow, Zeek, and Endpoint EDR telemetry via Kafka & ClickHouse.
- **Real-Time Detection Engine**: Streaming Sigma & YARA-L rule evaluation, ML-driven UEBA anomaly scoring, and sub-second alert generation.
- **Multi-Agent AI Investigation**: Graph-based investigation engine utilizing LLM agents for automated alert triage, MITRE ATT&CK mapping, and dynamic incident summary generation.
- **SOAR Orchestrator**: Closed-loop automated remediation engine with human-in-the-loop validation, automated containment playbooks, and 150+ n8n workflows.
- **Enterprise Knowledge Graph**: Neo4j graph model correlating entities (users, hosts, IP addresses, processes, domains) across time windows for blast radius analysis.
- **Threat Intelligence Exchange**: Bidirectional STIX/TAXII 2.1 integration, MISP sync, IOC scoring, and automated feed enrichment.
- **Modern Next.js SOC Dashboard**: Real-time SecOps command center with dark-mode visualization, live alert feeds, attack graphs, and incident management.

---

## 🏗️ Repository Structure

```
SKYNET/
├── backend/                  # FastAPI enterprise backend services
│   ├── app/
│   │   ├── api/v1/          # RESTful endpoints (alerts, incidents, threatintel, soar, etc.)
│   │   ├── core/            # Config, security, database engine
│   │   ├── models/          # SQLAlchemy & Pydantic domain models
│   │   └── services/        # Telemetry, correlation, investigation, LLM agent services
│   └── tests/               # Backend test suites
├── frontend/                 # Next.js 14 SOC command center UI
│   ├── src/                 # React components, pages, dashboard layouts
│   └── public/              # Static assets and icons
├── workflows/                # Comprehensive automation workflow collection
│   └── SKYNET_v5_ALL_150_N8N_WORKFLOWS/  # 150+ n8n enterprise SOAR workflows
└── docs/                     # Specifications & Architecture Blueprints
    ├── PRD.md               # Product Requirements Document
    ├── HLD.md               # High-Level Architecture Design
    ├── LLD.md               # Low-Level Design & Schemas
    ├── SRS.md               # Software Requirements Specification
    ├── RUNBOOK.md           # Operational Runbook
    ├── PLAYBOOK.md          # Incident Response Playbooks
    ├── THREAT_MODEL.md      # Threat Model & STRIDE Analysis
    └── TESTING_VALIDATION.md# Validation & QA Test Framework
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** & npm / yarn / pnpm
- **Docker & Docker Compose** (for PostgreSQL, Redis, ClickHouse, Neo4j, Kafka)

### Backend Setup

```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The SOC Command Center will be running at `http://localhost:3000`.

---

## 🛡️ License

This project is licensed under the MIT License - see the LICENSE file for details.
