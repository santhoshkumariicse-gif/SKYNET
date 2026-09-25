# SKYNET: Unified Master Product Specification & Architecture Blueprint (PRODUCT.md)
> **The Autonomous AI-Powered Security Operations Center (SOC) & Extended Detection & Response (XDR) Platform**  
> *Consolidated Enterprise Product Specification, Architecture Blueprint & Implementation Canon*

**Document Version:** 1.0.0-ENTERPRISE  
**Release Target:** SKYNET v1.0 (MVP) through v5.0 (Autonomous Active Defense)  
**System Designation:** SKYNET Core Platform  
**Repository Reference:** [d:/hackathon/hackex/SKYNET](file:///d:/hackathon/hackex/SKYNET)  
**Synthesized Canon Sources:**
- [SRS.md](file:///d:/hackathon/hackex/SKYNET/SRS.md) — Software Requirements Specification
- [MVP_ROADMAP.md](file:///d:/hackathon/hackex/SKYNET/MVP_ROADMAP.md) — MVP Product Requirements Document
- [ADD.md](file:///d:/hackathon/hackex/SKYNET/ADD.md) — Architectural Design Document
- [HLD.md](file:///d:/hackathon/hackex/SKYNET/HLD.md) — High-Level Design
- [LLD.md](file:///d:/hackathon/hackex/SKYNET/LLD.md) — Low-Level Design
- [DDD.md](file:///d:/hackathon/hackex/SKYNET/DDD.md) — Database Design Document
- [API_SPEC.md](file:///d:/hackathon/hackex/SKYNET/API_SPEC.md) — API Specifications & Integrations
- [THREAT_MODEL.md](file:///d:/hackathon/hackex/SKYNET/THREAT_MODEL.md) — Threat Model & Security Architecture
- [DEPLOYMENT.md](file:///d:/hackathon/hackex/SKYNET/DEPLOYMENT.md) — Infrastructure & Deployment Blueprint
- [TESTING_VALIDATION.md](file:///d:/hackathon/hackex/SKYNET/TESTING_VALIDATION.md) — Quality & Validation Framework
- [RUNBOOK.md](file:///d:/hackathon/hackex/SKYNET/RUNBOOK.md) — Site Reliability & Operations Runbook
- [PLAYBOOK.md](file:///d:/hackathon/hackex/SKYNET/PLAYBOOK.md) — SOC Incident Response Playbooks
- [VISION_ROADMAP.md](file:///d:/hackathon/hackex/SKYNET/VISION_ROADMAP.md) — Long-term Strategic Roadmap

---

## Table of Contents

1. [Executive Product Overview & Market Positioning](#1-executive-product-overview--market-positioning)
2. [Product Capabilities & Feature Matrix](#2-product-capabilities--feature-matrix)
3. [End-to-End System Architecture (C4 Topology)](#3-end-to-end-system-architecture-c4-topology)
4. [Autonomous SOC Pipeline: Raw Telemetry to Incident Remediation](#4-autonomous-soc-pipeline-raw-telemetry-to-incident-remediation)
5. [Polyglot Persistence Layer & Data Architecture](#5-polyglot-persistence-layer--data-architecture)
6. [Multi-Agent AI Investigation Engine](#6-multi-agent-ai-investigation-engine)
7. [Detection & Correlation Engines](#7-detection--correlation-engines)
8. [SOAR Active Defense & Human-in-the-Loop Orchestration](#8-soar-active-defense--human-in-the-loop-orchestration)
9. [API Gateway, Streaming & External Integrations](#9-api-gateway-streaming--external-integrations)
10. [Enterprise Security Architecture & Threat Model](#10-enterprise-security-architecture--threat-model)
11. [Deployment, Infrastructure & Sizing Blueprints](#11-deployment-infrastructure--sizing-blueprints)
12. [SRE Operations, Incident Playbooks & Verification](#12-sre-operations-incident-playbooks--verification)
13. [Codebase Scaffolding & Engineering Implementation Plan](#13-codebase-scaffolding--engineering-implementation-plan)

---

## 1. Executive Product Overview & Market Positioning

### 1.1 The Problem
Modern Security Operations Centers (SOCs) are overwhelmed by:
- **Alert Fatigue**: Over 10,000+ alerts daily per 1,000 endpoints; 70%+ are benign or false positives.
- **Analyst Burnout**: Tier-1 analysts spend 80% of their time manually copy-pasting IPs, hashes, and URLs into external threat lookups.
- **Dwell Time**: Average threat dwell time exceeds 200 days due to disconnected telemetry silos and slow manual investigation.
- **Skills Shortage**: 3.4 million cybersecurity workforce deficit globally.

### 1.2 The SKYNET Solution
**SKYNET** is an autonomous Tier-1 SOC and Extended Detection & Response (XDR) product that continuously ingests cross-platform telemetry, correlates distributed attack signals, executes multi-agent cognitive investigations, enriches IOCs across threat feeds, constructs microsecond-precision attack graphs, and formulates verified remediation proposals with cryptographic Human-in-the-Loop (HITL) safeguards.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             SKYNET PRODUCT VISION                           │
├───────────────────────┬─────────────────────────────┬───────────────────────┤
│    Continuous Sense   │      Cognitive Reason       │     Decisive Act      │
│  Sysmon, Auditd, PCAP │ LangGraph Multi-Agent Team  │ SOAR, Host Isolation  │
│  Syslog, CloudTrail   │ Dynamic MITRE ATT&CK Mapping│ Cryptographic Tokens  │
│  100k+ EPS Ingestion  │ Plain-Language Dossiers     │ Zero-Downtime Rollback│
└───────────────────────┴─────────────────────────────┴───────────────────────┘
```

### 1.3 Key Value Metrics
- **Mean Time to Detect (MTTD)**: Reduced from 4.2 hours to $< 15\text{ seconds}$.
- **Mean Time to Investigate (MTTI)**: Reduced from 45 minutes to $< 30\text{ seconds}$.
- **Analyst Triage Capacity**: Increased by $10\times$ without expanding headcount.
- **False Positive Dismissal**: $88\%$ autonomous suppression accuracy via contextual correlation.

---

## 2. Product Capabilities & Feature Matrix

| Functional Module | Tier-1 MVP (v1.0) | Mid-Tier (v2.0 - v3.0) | Enterprise Autonomous (v4.0 - v5.0) |
|---|---|---|---|
| **Telemetry Ingestion** | Windows Security, Sysmon, Syslog over HTTPS | CloudTrail, Kubernetes Audit, Linux Auditd, Zeek | Full Network PCAP, eBPF telemetry, IoT/OT protocols |
| **Detection Engine** | Sigma Rule Engine, Exact IOC Matching | Threshold Anomaly, Correlation Sliding Window | Transformer-based Sequence Anomaly, Real-time UEBA |
| **Threat Intelligence** | VirusTotal, AbuseIPDB, URLhaus, Local Redis | OpenCTI, MISP, AlienVault OTX, AlienVault pulses | Custom Threat Feeds, Private STIX/TAXII 2.1 Servers |
| **Investigation** | Automated Timeline Builder, Reverse Event Query | Multi-Hop Neo4j Attack Graph, Subnet Blast Radius | Multi-Agent Cognitive Swarm (LangGraph + Local LLMs) |
| **Case Management** | Incident Lifecycle, Evidence Locker, Notes | SLA timers, Shift Handover, CSV/JSON Exporter | WeasyPrint Executive PDF Reports, Board-Level KPIs |
| **Active Defense** | Advisory actions, manual execution script | One-click containment via Dashboard (HITL) | Autonomous low-risk containment, dual-key auth |
| **Deployment Model** | Single-Node Docker Compose | Multi-Node Kubernetes (On-Prem / Private Cloud) | Air-Gapped High-Availability Active-Active Cluster |

---

## 3. End-to-End System Architecture (C4 Topology)

SKYNET is engineered as a loosely coupled, resilient microservices ecosystem orchestrated via high-throughput message streaming and polyglot persistence:

```mermaid
flowchart TD
    subgraph Endpoints["Endpoints & Telemetry Sources"]
        W1["Windows PC / Laptop\n(Sysmon + WinEventLog)"]
        S1["Linux Server / Cloud VM\n(Auditd + Syslog)"]
        N1["Network Gateway\n(Firewall / Router Syslog)"]
    end

    subgraph IngestionLayer["Ingestion & Streaming (Port 8443 / 9092)"]
        LB["Envoy / NGINX Ingress\n(mTLS Termination)"]
        REC["FastAPI Telemetry Receiver\n(Schema Validation)"]
        KAFKA["Apache Kafka / Redpanda\n(telemetry.raw Topic)"]
    end

    subgraph ProcessingCore["Real-Time Processing Core"]
        NORM["OCSF/ECS Normalizer\n(Field Canonicalization)"]
        SIGMA["Detection Engine\n(Sigma Rules + IOC Matcher)"]
        CORR["Temporal Correlation Engine\n(Sliding Window Aggregator)"]
    end

    subgraph PersistenceLayer["Polyglot Persistence Layer"]
        CH[("ClickHouse\nTelemetry & Analytics")]
        PG[("PostgreSQL 16\nCases, Users, Evidence")]
        NEO[("Neo4j Graph DB\nAttack Entities & Topology")]
        REDIS[("Redis 7 Cluster\nIOC Cache & Session Store")]
    end

    subgraph AICore["Cognitive AI Tier (LangGraph Swarm)"]
        INV_AGENT["Investigation Agent\n(Root Cause & Evidence)"]
        SEV_AGENT["Severity Agent\n(Risk Scoring & Prioritization)"]
        REP_AGENT["Reporting Agent\n(Executive Dossiers)"]
    end

    subgraph ManagementApp["Presentation & Control Tier"]
        API["FastAPI Master Gateway\n(REST & WebSockets)"]
        DASH["Next.js 14 SOC Cockpit\n(Tailwind CSS + ShadCN UI)"]
        SOAR["SOAR Active Defense\n(Cryptographic HITL Gate)"]
    end

    Endpoints -->|Encrypted JSON over HTTPS| LB
    LB --> REC --> KAFKA
    KAFKA --> NORM
    NORM -->|Bulk Columnar Ingest| CH
    NORM -->|Streaming Pipeline| SIGMA
    SIGMA -->|Raw Alerts| CORR
    CORR -->|Incident Candidates| PG
    CORR -->|Trigger Webhook| INV_AGENT

    INV_AGENT <--> CH
    INV_AGENT <--> NEO
    INV_AGENT <--> REDIS
    INV_AGENT --> SEV_AGENT --> REP_AGENT
    REP_AGENT --> PG

    API <--> PG
    API <--> CH
    API <--> NEO
    API <--> REDIS
    DASH <-->|REST + WebSockets (Port 3000/8000)| API
    DASH -->|HITL Containment Approval| SOAR
    SOAR -->|Dispatch Remediation Script| Endpoints
```

---

## 4. Autonomous SOC Pipeline: Raw Telemetry to Incident Remediation

```
┌─────────────────┐     1. Telemetry Ingestion (Sysmon, Windows Event Logs, Syslog)
│ Raw Events      │ ──► Processed via HTTPS/mTLS receiver and buffered into Kafka.
└────────┬────────┘
         │
         ▼
┌─────────────────┐     2. Schema Normalization (OCSF / Elastic Common Schema)
│ Normalizer      │ ──► Maps disparate vendor fields into canonical JSON schema.
└────────┬────────┘
         │
         ▼
┌─────────────────┐     3. Real-Time Detection
│ Detection Engine│ ──► In-memory Sigma engine matches process creations, base64 flags.
└────────┬────────┘     Matches hashes, IPs, and domains against Redis IOC cache.
         │
         ▼
┌─────────────────┐     4. Temporal Correlation & Entity Clustering
│ Correlation Svc │ ──► Sliding window (60s) clusters multiple alerts by Host/User.
└────────┬────────┘     Suppresses duplicate signals, raises Incident Candidate.
         │
         ▼
┌─────────────────┐     5. Multi-Agent AI Investigation (LangGraph)
│ Cognitive Swarm │ ──► Queries ClickHouse for chronological microsecond timelines.
└────────┬────────┘     Traverses Neo4j for lateral movement paths.
         │              Enriches unranked IOCs via VirusTotal, AbuseIPDB, URLhaus.
         ▼
┌─────────────────┐     6. Incident Packaging & Evidence Locker
│ Case Manager    │ ──► Creates INC-2026-XXXX in PostgreSQL with linked evidence items.
└────────┬────────┘     Updates Attack Graph nodes in Neo4j.
         │
         ▼
┌─────────────────┐     7. Human-in-the-Loop Active Defense (SOAR)
│ SOC Cockpit UI  │ ──► Displays Executive Summary, MITRE Matrix, and Proposed Actions.
└─────────────────┘     Analyst approves Host Isolation or IP Block with 1-click token.
```

---

## 5. Polyglot Persistence Layer & Data Architecture

SKYNET avoids compromise by utilizing four purpose-built databases:

### 5.1 PostgreSQL 16 (Transactional State & Case Management)
Stores users, RBAC roles, alerts, incidents, evidence, audit logs, and HITL actions:

```sql
-- Core PostgreSQL DDL Snippet
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(64) UNIQUE NOT NULL,
    permissions JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role_id UUID NOT NULL REFERENCES roles(id),
    status VARCHAR(32) DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_number VARCHAR(32) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(16) NOT NULL, -- LOW, MEDIUM, HIGH, CRITICAL
    status VARCHAR(32) DEFAULT 'NEW', -- NEW, TRIAGED, INVESTIGATING, RESOLVED, CLOSED
    assigned_to UUID REFERENCES users(id),
    verdict VARCHAR(64) DEFAULT 'UNCONFIRMED', -- TRUE_POSITIVE, FALSE_POSITIVE
    ai_summary TEXT,
    ai_root_cause TEXT,
    ai_recommended_action TEXT,
    mitre_tactics JSONB DEFAULT '[]'::jsonb,
    mitre_techniques JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    evidence_type VARCHAR(64) NOT NULL, -- PROCESS_LOG, NETWORK_FLOW, FILE_HASH, IP_ADDRESS
    raw_payload JSONB NOT NULL,
    hash_sha256 VARCHAR(64),
    captured_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT
);

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id UUID REFERENCES users(id),
    action VARCHAR(128) NOT NULL,
    resource_type VARCHAR(64) NOT NULL,
    resource_id VARCHAR(128) NOT NULL,
    payload JSONB,
    client_ip VARCHAR(45) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 5.2 ClickHouse 24.x (High-Velocity Columnar Telemetry)
Handles 100,000+ EPS with sub-second temporal analytics:

```sql
CREATE DATABASE IF NOT EXISTS skynet;

CREATE TABLE skynet.telemetry_events (
    event_id UUID,
    event_timestamp DateTime64(6, 'UTC'),
    ingest_timestamp DateTime64(6, 'UTC') DEFAULT now64(6),
    host_name LowCardinality(String),
    host_ip IPv4,
    host_os LowCardinality(String),
    event_source LowCardinality(String), -- sysmon, windows_security, syslog
    event_id_code UInt32,
    process_id UInt32,
    process_name String,
    process_path String,
    process_command_line String,
    process_hash_sha256 FixedString(64),
    parent_process_id UInt32,
    parent_process_name String,
    parent_process_command_line String,
    user_name LowCardinality(String),
    user_domain LowCardinality(String),
    src_ip IPv4,
    src_port UInt16,
    dst_ip IPv4,
    dst_port UInt16,
    raw_payload String CODEC(ZSTD(3))
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_timestamp)
ORDER BY (event_timestamp, host_name, event_source, event_id_code)
TTL event_timestamp + INTERVAL 90 DAY;
```

### 5.3 Neo4j 5.x (Property Graph for Attack Paths & Blast Radius)
- **Node Labels**: `:Host`, `:User`, `:Process`, `:File`, `:IPAddress`, `:Domain`, `:Alert`, `:Incident`
- **Relationship Types**: `(:Process)-[:SPAWNED]->(:Process)`, `(:Process)-[:CONNECTED_TO]->(:IPAddress)`, `(:User)-[:LOGGED_INTO]->(:Host)`, `(:Alert)-[:IMPLICATES]->(:Host)`

### 5.4 Redis 7 (In-Memory Fast Lookups & Ephemeral State)
- `ioc:hash:<sha256>`: JSON cache containing VT score and malicious verdicts (TTL: 86400s)
- `ioc:ip:<ipv4>`: AbuseIPDB score and country code (TTL: 43200s)
- `session:blacklist:<jwt_jti>`: Active token revocation (TTL: token expiry)
- `rate_limit:<client_ip>`: Sliding window counters

---

## 6. Multi-Agent AI Investigation Engine

Built upon **LangGraph**, the autonomous AI tier functions as an iterative cognitive reasoning swarm:

```
                    ┌────────────────────────────┐
                    │      Alert Ingestion       │
                    └─────────────┬──────────────┘
                                  │
                                  ▼
                    ┌────────────────────────────┐
                    │    Investigation Agent     │
                    │ - Query ClickHouse timeline│
                    │ - Traverse Neo4j graph     │
                    │ - Call VT / AbuseIPDB      │
                    └─────────────┬──────────────┘
                                  │
                                  ▼
                    ┌────────────────────────────┐
                    │       Severity Agent       │
                    │ - Calibrate Asset Value    │
                    │ - Score Contextual Risk    │
                    │ - Classify False Positives │
                    └─────────────┬──────────────┘
                                  │
                                  ▼
                    ┌────────────────────────────┐
                    │      Reporting Agent       │
                    │ - Executive Brief          │
                    │ - Technical Root Cause     │
                    │ - Remediation Checklist    │
                    └─────────────┬──────────────┘
                                  │
                                  ▼
                    ┌────────────────────────────┐
                    │ Case Finalization & Dossier│
                    └────────────────────────────┘
```

### Agent State Schema
```python
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class AgentInvestigationState(BaseModel):
    alert_id: str
    incident_number: Optional[str] = None
    entities: Dict[str, List[str]] # {'ips': [...], 'hashes': [...], 'hosts': [...]}
    threat_intel_results: Dict[str, Any] = {}
    chronological_timeline: List[Dict[str, Any]] = []
    attack_graph_paths: List[Dict[str, Any]] = []
    confidence_score: float = 0.0
    recommended_severity: str = "MEDIUM"
    is_false_positive: bool = False
    executive_summary: str = ""
    technical_root_cause: str = ""
    mitre_mappings: List[str] = []
    suggested_actions: List[Dict[str, Any]] = []
```

---

## 7. Detection & Correlation Engines

### 7.1 Sigma Rule Engine
Compiles standard YAML Sigma rules into real-time executable Python filter functions and ClickHouse SQL queries:
- **Rule Categories**: Execution, Persistence, Privilege Escalation, Defense Evasion, Credential Access, Lateral Movement, Exfiltration.
- **Critical MVP Rules**:
  - `sigma_win_powershell_base64`: Matches encoded `-enc` or `-EncodedCommand`.
  - `sigma_win_mimikatz_dump`: Matches `lsass.exe` process access with mask `0x1010` / `0x1038`.
  - `sigma_win_brute_force`: Aggregates 5+ failed logons (`Event ID 4625`) within 60s per user/host.
  - `sigma_network_malicious_ip`: Checks connection destinations against threat intelligence.

### 7.2 Correlation Engine
- **Sliding Window**: 60-second in-memory stateful tumbling window.
- **Entity Graph Linkage**: Automatically correlates alerts sharing identical `host_name`, `user_name`, or parent process GUIDs.
- **Deduplication**: Automatically groups identical alert signatures within 15 minutes to eliminate redundant notification spikes.

---

## 8. SOAR Active Defense & Human-in-the-Loop Orchestration

### 8.1 Containment Actions
1. **Network Host Isolation**: Dispatches firewall rule command to block all inbound and outbound IP traffic on the target host except the management tunnel to SKYNET (TCP 8443).
2. **Account Disablement**: Triggers active directory / local account lock to revoke compromised credentials.
3. **Process Termination**: Terminates malicious PID trees identified in the investigation timeline.
4. **Firewall Perimeter Block**: Injects malicious C2 IP/domain into border firewall / router access control list.

### 8.2 Dual-Key & Cryptographic Verification
High-risk containment actions cannot be executed autonomously without human validation:
1. AI proposes containment action + rollback procedure in the SOC Dashboard.
2. Analyst clicks **Approve Containment**.
3. Gateway validates analyst JWT role (`ADMIN` or `L1_ANALYST` with `soar:execute`).
4. Action is cryptographically signed and logged into immutable `audit_logs` table.
5. In case of disruption, an automated **1-Click Rollback Script** is pre-computed and stored.

---

## 9. API Gateway, Streaming & External Integrations

### 9.1 API Overview & Route Map
The backend exposes RESTful endpoints and real-time WebSockets under `/api/v1`:

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/v1/auth/login` | Issue JWT access & refresh tokens | None (Public) |
| `POST` | `/api/v1/auth/refresh` | Refresh expired access token | Refresh Token |
| `POST` | `/api/v1/auth/logout` | Revoke session into Redis blacklist | Bearer Token |
| `POST` | `/api/v1/telemetry/ingest` | High-throughput telemetry batch ingestion | Agent API Key |
| `GET` | `/api/v1/alerts` | Paginated alert feed with severity filters | Bearer Token |
| `GET` | `/api/v1/alerts/{id}` | Detailed alert breakdown | Bearer Token |
| `GET` | `/api/v1/incidents` | Incident list with status & assignment | Bearer Token |
| `POST` | `/api/v1/incidents` | Create manual or automated incident | Bearer Token |
| `GET` | `/api/v1/incidents/{id}` | Full incident dossier, evidence, & AI report | Bearer Token |
| `PATCH` | `/api/v1/incidents/{id}/status` | Transition case state (NEW -> CLOSED) | Bearer Token |
| `GET` | `/api/v1/investigation/{id}/timeline` | Chronological event timeline | Bearer Token |
| `GET` | `/api/v1/threatintel/lookup` | Query VT / AbuseIPDB / URLhaus cache | Bearer Token |
| `POST` | `/api/v1/soar/execute` | Execute approved containment action | Admin Bearer Token |
| `WS` | `/api/v1/ws/live-events` | Real-time WebSocket event/alert stream | WebSocket Token |

---

## 10. Enterprise Security Architecture & Threat Model

### 10.1 STRIDE Threat Matrix & Mitigations
- **Spoofing**: Mitigated by Mutual TLS (mTLS) for agents, HMAC-SHA256 agent authentication headers, and Argon2id user password hashing.
- **Tampering**: Telemetry hashes (SHA256) computed at collection time; append-only ClickHouse partitions and immutable PostgreSQL audit logs.
- **Repudiation**: Every action, status change, and containment trigger is logged with client IP, timestamp, actor ID, and original payload.
- **Information Disclosure**: AES-256 encryption at rest; TLS 1.3 in transit; sensitive threat intel API keys encrypted in vault.
- **Denial of Service**: Redis token-bucket rate limiters; Kafka buffering absorb ingestion bursts up to 250,000 EPS.
- **Elevation of Privilege**: Strict Role-Based Access Control (RBAC); SOAR endpoints enforce dual authorization checks.

---

## 11. Deployment, Infrastructure & Sizing Blueprints

### 11.1 Deployment Profiles

| Profile | Target Capacity | CPU / RAM | Storage | Deploy Method |
|---|---|---|---|---|
| **Development / Lab** | 10–50 Endpoints (1k EPS) | 8 vCPU / 16 GB RAM | 250 GB SSD | Single-Node Docker Compose |
| **Enterprise Standard** | 500–2,500 Endpoints (25k EPS) | 32 vCPU / 64 GB RAM | 2 TB NVMe | Kubernetes (3-node cluster) |
| **Global Enterprise** | 10,000+ Endpoints (100k+ EPS) | 128 vCPU / 256 GB RAM | 20 TB NVMe + S3 | Multi-Node K8s + ClickHouse Cluster |

### 11.2 Standard Port Map
- **Frontend Dashboard (Next.js)**: Port `3000`
- **Backend API Gateway (FastAPI)**: Port `8000`
- **Telemetry Ingestion Ingress**: Port `8443`
- **PostgreSQL Database**: Port `5432`
- **Redis Cache & Session**: Port `6379`
- **ClickHouse HTTP / Native**: Port `8123` / `9000`
- **Neo4j Browser / Bolt**: Port `7474` / `7687`
- **Apache Kafka Broker**: Port `9092`

---

## 12. SRE Operations, Incident Playbooks & Verification

### 12.1 Standard SOC Response Playbooks (PLAYBOOK.md Canon)
1. **Playbook Alpha — Ransomware / Bulk Encryption**:
   - Indicator: High-frequency file rename events (`.locked`, `.crypt`) + shadow copy deletion (`vssadmin delete shadows`).
   - Automated Actions: Trigger severity `CRITICAL`; propose immediate host network isolation; preserve memory dump.
2. **Playbook Bravo — Credential Stuffing & Password Spray**:
   - Indicator: $\ge 20$ failed logon attempts from single external IP across multiple usernames within 3 minutes.
   - Automated Actions: Ingest external IP to firewall blocklist; temporarily lock targeted local accounts; notify analyst.
3. **Playbook Charlie — Suspicious Living-off-the-Land (LotL) Binary**:
   - Indicator: `certutil.exe -urlcache -split -f` or `bitsadmin.exe` downloading executable files.
   - Automated Actions: Hash download URL; query VirusTotal; flag process tree in incident timeline.

---

## 13. Codebase Scaffolding & Engineering Implementation Plan

To turn these 13 specifications into a functional product, the workspace is organized into a clean, modular monorepo:

```
d:/hackathon/hackex/SKYNET/
├── docker-compose.yml           # Unified local multi-service container orchestration
├── .env.example                 # Standardized environment configuration template
├── README.md                    # Product quickstart, installation, and architecture
│
├── backend/                     # FastAPI Asynchronous Core
│   ├── app/
│   │   ├── main.py              # Application factory & lifespan setup
│   │   ├── core/                # Configuration, logging, security (JWT/Argon2)
│   │   ├── db/                  # Database session engines (SQLite/Postgres, Redis)
│   │   ├── models/              # SQLAlchemy database ORM models
│   │   ├── schemas/             # Pydantic v2 validation contracts
│   │   ├── api/                 # Versioned route controllers (/auth, /alerts, /incidents)
│   │   ├── services/            # Telemetry normalization, threat intel, correlation
│   │   ├── detection/           # Sigma rules engine & IOC matcher
│   │   └── ai_agents/           # Cognitive investigation & report generator
│   ├── requirements.txt         # Production backend dependencies
│   └── tests/                   # Pytest test suite
│
├── frontend/                    # Next.js 14 SOC Cockpit Dashboard
│   ├── app/                     # App router pages (Alerts, Incidents, Threat Map)
│   ├── components/              # UI components (Kanban, Timeline, Stats, Matrix)
│   ├── lib/                     # API client, WebSocket client, state store
│   └── package.json             # Frontend dependencies (React, Tailwind, Lucide)
│
└── agent/                       # Python Cross-Platform Telemetry Agent
    ├── agent.py                 # Telemetry collector (CPU, RAM, Processes, Sysmon)
    ├── config.yaml              # Agent polling intervals & gateway endpoint
    └── requirements.txt         # psutil, requests, cryptography
```

---
*SKYNET Platform Canon Approved — Ready for Immediate Codebase Implementation.*
