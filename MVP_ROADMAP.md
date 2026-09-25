# SKYNET MVP: Product Requirements Document (PRD) & Roadmap
> **Autonomous Tier-1 SOC Analyst Platform | Version 1.0**

**System Designation:** SKYNET MVP Core  
**Document Version:** 1.0  
**Status:** Approved for Implementation  
**Primary Repository Reference:** [SKYNET Workspace](file:///d:/hackathon/hackex/SKYNET)  
**Parent Specifications:** [SRS.md](file:///d:/hackathon/hackex/SKYNET/SRS.md) | [ROADMAP.md](file:///d:/hackathon/hackex/SKYNET/ROADMAP.md) | [SKYNET_All_Phases.md](file:///d:/hackathon/hackex/SKYNET/SKYNET_All_Phases.md)

---

## Table of Contents

1. [Executive Summary & MVP Vision](#1-executive-summary--mvp-vision)
2. [MVP Scope & Boundary Matrix](#2-mvp-scope--boundary-matrix)
3. [End-to-End MVP Architecture & Data Flow](#3-end-to-end-mvp-architecture--data-flow)
4. [Technology Stack & Framework Selection](#4-technology-stack--framework-selection)
5. [MVP Deliverables: Module-by-Module Specification](#5-mvp-deliverables-module-by-module-specification)
   - [Module 1: Authentication, RBAC & User Management](#module-1-authentication-rbac--user-management)
   - [Module 2: Log Collection, Event Storage & Normalization](#module-2-log-collection-event-storage--normalization)
   - [Module 3: Detection Engine & Rule Processing](#module-3-detection-engine--rule-processing)
   - [Module 4: Threat Intelligence & Automated IOC Enrichment](#module-4-threat-intelligence--automated-ioc-enrichment)
   - [Module 5: Investigation Engine, Timeline Builder & MITRE Mapping](#module-5-investigation-engine-timeline-builder--mitre-mapping)
   - [Module 6: Incident Management & Case Lifecycle](#module-6-incident-management--case-lifecycle)
   - [Module 7: Autonomous AI SOC Analyst Agent](#module-7-autonomous-ai-soc-analyst-agent)
   - [Module 8: Command & Control Dashboard](#module-8-command--control-dashboard)
6. [Sprint Execution Plan & Timeline](#6-sprint-execution-plan--timeline)
7. [MVP Success Criteria & Acceptance Sign-off Matrix](#7-mvp-success-criteria--acceptance-sign-off-matrix)
8. [Docker Compose MVP Deployment Blueprint](#8-docker-compose-mvp-deployment-blueprint)
9. [Deferred Features & Post-MVP Evolution (v2.0+)](#9-deferred-features--post-mvp-evolution-v20)

---

## 1. Executive Summary & MVP Vision

### 1.1 Goal
The primary objective of the **SKYNET MVP** is to engineer and deploy a fully operational **Autonomous Tier-1 SOC Analyst**. The system automates the most time-consuming responsibilities of Level-1 security analysts:
1. Ingesting raw security event streams from target machines.
2. Evaluating threats via Sigma rules and known IOC matching.
3. Automatically enriching discovered Indicators of Compromise (hashes, IPs, domains) across global threat feeds.
4. Investigating correlated attack events and constructing causality timelines.
5. Packaging correlated alerts into tracked Incident Cases with evidence items.
6. Generating plain-language executive summaries, root cause explanations, and human-in-the-loop response suggestions.

```
                    ┌───────────────────────────────────────┐
                    │        RAW ENDPOINT TELEMETRY         │
                    │   Windows Events │ Sysmon │ Syslog   │
                    └───────────────────┬───────────────────┘
                                        │
                                        ▼
                    ┌───────────────────────────────────────┐
                    │      SKYNET MVP TIER-1 AI SOC         │
                    │   Detect ➔ Enrich ➔ Correlate         │
                    │   Investigate ➔ Timeline ➔ Incident   │
                    └───────────────────┬───────────────────┘
                                        │
                                        ▼
                    ┌───────────────────────────────────────┐
                    │      HUMAN SOC ANALYST COCKPIT        │
                    │   Review AI Findings & Approve Plan   │
                    └───────────────────────────────────────┘
```

---

## 2. MVP Scope & Boundary Matrix

To ensure rapid delivery, high stability, and rigorous focus, the MVP establishes explicit boundaries:

### 2.1 Included in MVP Scope
- **Telemetry Collection**:
  - Windows Security & System Event Logs (Event IDs: 4624, 4625, 4720, 7045).
  - Microsoft Sysmon Logs (Event IDs: 1 Process Create, 3 Network Connect, 10 Process Access, 11 File Create).
  - RFC 5424 Syslog stream ingestion (Firewall & Linux auth).
- **Threat Intelligence**:
  - VirusTotal v3 API (SHA256, MD5, IP lookups).
  - AbuseIPDB v2 API (Public IPv4 abuse confidence scoring).
  - URLhaus API (Active malware distribution URLs).
  - Local caching in Redis to prevent API quota exhaustion.
- **Threat Detection**:
  - Brute Force Login Detection ($\ge 5$ failures within 60s).
  - Suspicious PowerShell / Command Execution (Base64 encoding, download cradles, bypass flags).
  - Malicious External IP Communication (matches against threat intel feeds).
  - Internal Port Scanning ($\ge 20$ distinct destination ports in 10s).
- **Investigation Capabilities**:
  - Chronological Timeline Builder aligning microsecond timestamps.
  - Automatic IOC Contextualization.
  - Related Event Search linking shared User, Host, and Process trees.
- **AI Security Analyst**:
  - Autonomous Investigation Agent built using LangGraph.
  - Dynamic Severity Recommendation (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
  - Executive Incident Summary & Technical Root Cause generation.
  - Contextual Response Suggestions (advisory actions).
- **Case Management**:
  - Incident Case Creation with auto-incrementing identifiers (`INC-2026-XXXX`).
  - Status Tracking (`NEW`, `TRIAGED`, `INVESTIGATING`, `RESOLVED`, `CLOSED`).
  - Evidence Locker storing raw event IDs, memory artifacts, and analyst notes.
- **Unified Web Dashboard**:
  - Live Alert Feed with severity badges.
  - Incident Kanban & Detail Investigation view.
  - Threat Intelligence Overview & Global KPI metrics.

### 2.2 Explicitly Out of Scope (Deferred to Version 2.0+)
- **Autonomous Endpoint Isolation & Active Intervention**: No automated endpoint network cutting or direct host process killing without manual sysadmin action.
- **EDR Kernel Driver**: No proprietary Windows Kernel Mode Driver (ELAM / Minifilter) or eBPF kernel hooks in MVP.
- **Proactive Threat Hunting Engine**: No background hypothesis-driven historical sweep agents.
- **Multi-Tenant SaaS Architecture**: MVP is strictly single-tenant for enterprise or dedicated lab deployment.
- **Enterprise MDR Operations**: No multi-customer ticketing integrations (ServiceNow, Jira Service Desk) in MVP.

---

## 3. End-to-End MVP Architecture & Data Flow

```mermaid
flowchart TD
    subgraph ClientEndpoints["Client Endpoints"]
        WA["Windows Agent\n(Sysmon + Windows Event Logs)"]
        SYSLOG["Syslog Device / Forwarder\n(Firewall / Linux Auth)"]
    end

    subgraph Messaging["Streaming & Ingestion"]
        KAFKA["Apache Kafka / Redpanda\nTopic: telemetry.raw"]
    end

    subgraph Persistence["High-Performance Storage"]
        CH[("ClickHouse Columnar DB\nevents_normalized")]
        PG[("PostgreSQL 16\nUsers, Alerts, Incidents")]
        NEO[("Neo4j Graph Database\nAttack Entity Paths")]
        REDIS[("Redis 7 Cache\nIOC Cache & Session Store")]
    end

    subgraph DetectionLayer["Detection & Routing"]
        NORM["Normalization Service\n(Parses ECS/OCSF Schema)"]
        DETECTION["Detection Engine\n(Sigma Rules + IOC Matching)"]
    end

    subgraph Orchestration["Agentic Orchestration"]
        N8N["n8n Workflow Engine\n(Alert Webhook Router)"]
        AI_AGENT["AI Investigation Agent\n(LangGraph + OpenAI / Local LLM)"]
        THREAT_SVC["Threat Intel Integrations\n(VirusTotal, AbuseIPDB, URLhaus, OpenCTI)"]
    end

    subgraph Management["Case Management & UI"]
        INC_MGR["Incident Manager\n(FastAPI Core Backend)"]
        DASH["Command Dashboard\n(Next.js 14 + Tailwind CSS)"]
    end

    WA & SYSLOG -->|Encrypted JSON over HTTPS| KAFKA
    KAFKA --> NORM
    NORM -->|Bulk Write| CH
    NORM -->|Stream Events| DETECTION

    DETECTION -->|Triggered Alerts| PG
    DETECTION -->|Alert Webhook| N8N

    N8N -->|Trigger Investigation| AI_AGENT
    AI_AGENT <-->|Query Events & Timelines| CH
    AI_AGENT <-->|Query Entity Relationships| NEO
    AI_AGENT <-->|Enrich Hashes & IPs| THREAT_SVC
    THREAT_SVC <--> REDIS

    AI_AGENT -->|Synthesized Dossier| INC_MGR
    INC_MGR -->|Persist Incident & Evidence| PG
    INC_MGR -->|Update Attack Graph| NEO

    DASH <-->|REST API & WebSockets| INC_MGR
```

---

## 4. Technology Stack & Framework Selection

| Layer | Technology | Version | Rationale & Selection Criteria |
|---|---|---|---|
| **Frontend UI** | Next.js + React | 14.x / 18.x | Server-Side Rendering (SSR), App Router, dynamic routing, high-performance dashboards. |
| **Styling & UI Kit** | Tailwind CSS + ShadCN UI | 3.4+ | Modern, sleek dark-mode aesthetics, responsive layouts, accessible UI components. |
| **Backend API Gateway**| FastAPI (Python) | 0.110+ | Asynchronous async/await execution, native Pydantic v2 validation, auto-generated OpenAPI documentation. |
| **Workflow Engine** | n8n | Latest | Visual multi-step orchestration, flexible webhook handling, rapid agent integration without custom pipeline boilerplate. |
| **AI Agentic Framework**| LangGraph / LangChain | 0.1+ | Stateful multi-actor orchestration, cyclic reasoning loops, strict schema enforcement. |
| **Inference Models** | OpenAI (GPT-4o) / Local LLM | API / Ollama | Deep contextual cybersecurity reasoning; supports local fallback (Llama-3-70B, DeepSeek-R1). |
| **Relational Store** | PostgreSQL | 16.x | ACID-compliant storage for users, authentication, case state, evidence metadata, and audit records. |
| **Telemetry Store** | ClickHouse | 24.x | Columnar storage achieving 100k+ EPS ingestion with sub-second analytical aggregations across billions of rows. |
| **Attack Graph** | Neo4j Community | 5.x | Native property graph engine for modeling and traversing complex multi-hop adversary attack paths. |
| **Cache & Queue** | Redis | 7.x Alpine | In-memory key-value cache for threat lookups, rate limiting, and temporary blackboard storage. |
| **Threat Feeds** | OpenCTI, MISP, VT, AbuseIPDB | REST APIs | Industry-standard threat intelligence exchange platforms and public reputation APIs. |
| **Containerization** | Docker & Docker Compose | 26.x / 2.27+ | Single-command local and production multi-container orchestration. |

---

## 5. MVP Deliverables: Module-by-Module Specification

### Module 1: Authentication, RBAC & User Management
- **Deliverables**:
  - Secure JWT-based authentication system with salted password hashing (Argon2id / bcrypt).
  - Role-Based Access Control enforcing two core roles: `ANALYST` (triage, review, add notes) and `ADMIN` (configure rules, users, API keys).
  - User session management with Redis token blacklisting for immediate revocation.
- **REST Endpoints**:
  - `POST /api/v1/auth/login`: Issue access and refresh tokens.
  - `POST /api/v1/auth/logout`: Revoke active session.
  - `GET /api/v1/users/me`: Return current user profile and permission scope.

### Module 2: Log Collection, Event Storage & Normalization
- **Deliverables**:
  - Python-based Windows telemetry agent (`agent/windows_agent.py`) capturing Windows Event Logs and Sysmon channels.
  - Ingestion receiver pushing incoming logs to Kafka topic `telemetry.raw`.
  - Normalization worker parsing raw events into Elastic Common Schema (ECS) formatted JSON.
  - ClickHouse schema `skynet.events_normalized` partitioned monthly with ZSTD compression.

```sql
-- ClickHouse MVP Normalized Events Table
CREATE TABLE IF NOT EXISTS skynet.events_normalized (
    event_timestamp DateTime64(6, 'UTC'),
    event_id UUID,
    event_type LowCardinality(String), -- 'process_create', 'network_connect', 'logon'
    device_uuid LowCardinality(String),
    device_hostname String,
    user_name String,
    process_name String,
    process_command_line String,
    process_hash_sha256 FixedString(64),
    destination_ip IPv4,
    destination_port UInt16,
    mitre_technique_id LowCardinality(String),
    raw_payload String CODEC(ZSTD(3))
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_timestamp)
ORDER BY (event_type, event_timestamp, device_uuid);
```

### Module 3: Detection Engine & Rule Processing
- **Deliverables**:
  - Real-time rule evaluator checking normalized streams against pre-configured detection rules:
    1. **Rule 101 - Brute Force**: $\ge 5$ Event ID 4625 (Logon Failure) within 60s for target account.
    2. **Rule 102 - Suspicious PowerShell**: Process command line contains `-enc`, `downloadstring`, or `bypass`.
    3. **Rule 103 - Malicious IP Connection**: Destination IP matches active malicious IP set.
    4. **Rule 104 - Internal Port Scan**: Host initiates TCP SYN attempts to $\ge 20$ unique ports on a subnet within 10s.
  - Alert records persisted to PostgreSQL `alerts` table and emitted via webhook to n8n.

### Module 4: Threat Intelligence & Automated IOC Enrichment
- **Deliverables**:
  - Asynchronous enrichment service connecting to:
    - **VirusTotal v3**: File hashes and domains.
    - **AbuseIPDB v2**: External IPv4 addresses.
    - **URLhaus**: Discovered URLs in command lines or logs.
  - Redis cache layer holding enriched verdicts (TTL: 24h for hashes, 6h for IPs) to prevent API rate exhaustion.
  - Normalized Composite Threat Score calculation ($0–100$) embedded into the alert payload.

### Module 5: Investigation Engine, Timeline Builder & MITRE Mapping
- **Deliverables**:
  - Chronological Timeline Builder querying ClickHouse for all events associated with the flagged host and user within a $T \pm 15\text{ minute}$ window of the detection.
  - MITRE ATT&CK Mapper assigning verified technique IDs (e.g., T1059.001 PowerShell, T1110 Brute Force, T1071 C2).
  - Neo4j entity graph updater populating nodes (`:User`, `:Device`, `:Process`, `:IP`) and relationship edges.

### Module 6: Incident Management & Case Lifecycle
- **Deliverables**:
  - Full case management system in PostgreSQL tracking incident lifecycle: `NEW` $\rightarrow$ `TRIAGED` $\rightarrow$ `INVESTIGATING` $\rightarrow$ `RESOLVED` $\rightarrow$ `CLOSED`.
  - Evidence Locker linking specific ClickHouse `event_id` records, threat enrichment JSONs, and analyst notes to the case.
  - REST endpoints for case triage, assignment, note addition, and status transitions.

### Module 7: Autonomous AI SOC Analyst Agent
- **Deliverables**:
  - LangGraph state machine powered by OpenAI GPT-4o or local LLM (Ollama).
  - Autonomous reasoning cycle:
    1. Read alert metadata and timeline events.
    2. Request additional host and IOC context via MCP tools.
    3. Identify attacker kill-chain stage.
    4. Generate a human-readable **Executive Summary**.
    5. Detail the technical **Root Cause Analysis**.
    6. Recommend a prioritized **Remediation Action Plan** for human review.
  - Strict Pydantic JSON validation ensuring zero hallucinated schemas.

### Module 8: Command & Control Dashboard
- **Deliverables**:
  - Modern Next.js 14 web application styled with Tailwind CSS and ShadCN.
  - **Live Alert Feed**: Real-time table of incoming alerts with severity indicators and instant triage buttons.
  - **Incident Workspace**: Split-screen interface displaying attack timelines, AI summaries, MITRE technique badges, and evidence tables.
  - **Threat Intelligence Modal**: Interactive drill-down displaying VirusTotal and AbuseIPDB reputation details.
  - **Executive KPI Cards**: Real-time counts of open incidents, active compromised hosts, and MTTD/MTTR averages.

---

## 6. Sprint Execution Plan & Timeline

The MVP implementation is structured into **6 iterative two-week engineering sprints**:

```mermaid
gantt
    title SKYNET MVP Implementation Roadmap (12 Weeks)
    dateFormat  YYYY-MM-DD
    section Sprint 1
    Core Infra, DBs & Auth (Mod 1)      :done, s1_1, 2026-10-01, 14d
    Agent Ingestion & Storage (Mod 2)    :done, s1_2, 2026-10-01, 14d
    section Sprint 2
    Normalization Pipeline (Mod 2)      :active, s2_1, 2026-10-15, 14d
    Detection Engine Rules (Mod 3)       :active, s2_2, 2026-10-15, 14d
    Threat Intel & Redis Cache (Mod 4)  :active, s2_3, 2026-10-15, 14d
    section Sprint 3
    Timeline Builder Engine (Mod 5)     :s3_1, 2026-10-29, 14d
    Neo4j Attack Graph Integration (Mod 5):s3_2, 2026-10-29, 14d
    MITRE ATT&CK Mapper (Mod 5)         :s3_3, 2026-10-29, 14d
    section Sprint 4
    Case Management Core (Mod 6)        :s4_1, 2026-11-12, 14d
    LangGraph AI SOC Analyst (Mod 7)    :s4_2, 2026-11-12, 14d
    Evidence Locker Integration (Mod 6) :s4_3, 2026-11-12, 14d
    section Sprint 5
    Next.js UI & Alert Feed (Mod 8)     :s5_1, 2026-11-26, 14d
    Incident Workspace & Timeline View (Mod 8):s5_2, 2026-11-26, 14d
    End-to-End n8n Pipeline Sync        :s5_3, 2026-11-26, 14d
    section Sprint 6
    Red Team Attack Simulation Validation:s6_1, 2026-12-10, 14d
    Bug Fixes, Performance & Final Signoff:s6_2, 2026-12-10, 14d
```

---

## 7. MVP Success Criteria & Acceptance Sign-off Matrix

The SKYNET MVP will be certified as production-ready upon passing the **End-to-End Autonomous Lifecycle Test**:

```
[Simulated Attack] ➔ [1. Alert Received] ➔ [2. IOC Enriched] ➔ [3. Timeline Generated]
                   ➔ [4. Incident Created] ➔ [5. Report Generated] ➔ [6. Analyst Sign-Off]
```

| Step | Milestone Stage | Acceptance Verification Criteria | Status |
|:---:|---|---|:---:|
| **1** | **Alert Received** | Ingest simulated suspicious PowerShell script via agent; verify alert triggers within 5 seconds with correct rule metadata. | `[ ]` |
| **2** | **IOC Enriched** | Confirm destination IP and script hash are queried across VirusTotal and AbuseIPDB, returning normalized score and cached in Redis. | `[ ]` |
| **3** | **Timeline Generated** | Verify investigation engine queries ClickHouse and orders parent process, script launch, and network connection chronologically. | `[ ]` |
| **4** | **Incident Created** | Confirm correlated alert is automatically promoted to an active Incident Case in PostgreSQL with assigned identifier (`INC-2026-XXXX`). | `[ ]` |
| **5** | **Report Generated** | AI SOC Analyst generates verified JSON dossier containing executive summary, root cause, MITRE T1059.001 tag, and recommended response. | `[ ]` |
| **6** | **Analyst Review** | Human SOC Analyst logs into Next.js dashboard, reviews timeline and AI summary, clicks "Approve Recommendation", and closes incident. | `[ ]` |

---

## 8. Docker Compose MVP Deployment Blueprint

The complete MVP infrastructure is deployed via a unified `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: skynet-mvp-postgres
    restart: always
    environment:
      POSTGRES_USER: skynet_admin
      POSTGRES_PASSWORD: SkynetMVPPass2026!
      POSTGRES_DB: skynet_db
    ports:
      - "5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U skynet_admin -d skynet_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  clickhouse:
    image: clickhouse/clickhouse-server:24.3-alpine
    container_name: skynet-mvp-clickhouse
    restart: always
    ports:
      - "8123:8123" # HTTP API
      - "9000:9000" # Native Client
    volumes:
      - ch_data:/var/lib/clickhouse
    ulimits:
      nofile:
        soft: 262144
        hard: 262144

  redis:
    image: redis:7-alpine
    container_name: skynet-mvp-redis
    restart: always
    ports:
      - "6379:6379"

  neo4j:
    image: neo4j:5.18-community
    container_name: skynet-mvp-neo4j
    restart: always
    ports:
      - "7474:7474" # Web Browser
      - "7687:7687" # Bolt Protocol
    environment:
      - NEO4J_AUTH=neo4j/SkynetNeo4jPass2026!
    volumes:
      - neo4j_data:/data

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: skynet-mvp-backend
    restart: always
    depends_on:
      postgres:
        condition: service_healthy
      clickhouse:
        condition: service_started
      redis:
        condition: service_started
      neo4j:
        condition: service_started
    environment:
      DATABASE_URL: postgresql+asyncpg://skynet_admin:SkynetMVPPass2026!@postgres:5432/skynet_db
      CLICKHOUSE_URL: http://clickhouse:8123
      REDIS_URL: redis://redis:6379/0
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_USER: neo4j
      NEO4J_PASSWORD: SkynetNeo4jPass2026!
      OPENAI_API_KEY: ${OPENAI_API_KEY:-}
      VIRUSTOTAL_API_KEY: ${VIRUSTOTAL_API_KEY:-}
      ABUSEIPDB_API_KEY: ${ABUSEIPDB_API_KEY:-}
    ports:
      - "8000:8000"

  n8n:
    image: docker.n8n.io/n8nio/n8n:latest
    container_name: skynet-mvp-n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=SkynetN8nAdmin2026!
      - WEBHOOK_URL=http://localhost:5678/
    volumes:
      - n8n_data:/home/node/.n8n

  dashboard:
    build:
      context: ./dashboard
      dockerfile: Dockerfile
    container_name: skynet-mvp-dashboard
    restart: always
    depends_on:
      - backend
    ports:
      - "3000:80"

volumes:
  pg_data:
  ch_data:
  neo4j_data:
  n8n_data:
```

---

## 9. Deferred Features & Post-MVP Evolution (v2.0+)

Following the successful deployment and sign-off of the MVP, the following advanced capabilities are scheduled for the **Version 2.0+ Release Cycle**:

1. **Autonomous Endpoint Active Containment**: Integration with endpoint firewall and process termination APIs to execute machine-speed containment without manual analyst intervention.
2. **Custom EDR Kernel Driver**: Development of a specialized Windows Minifilter / ELAM driver and Linux eBPF telemetry sensor for deeper memory inspection.
3. **Continuous AI Threat Hunting Engine**: Autonomous background agents executing retrospective query sweeps across months of ClickHouse cold data to uncover stealthy persistence.
4. **Multi-Tenant MSSP Partitioning**: Complete logical and database-level isolation enabling security service providers to serve multiple client organizations from a single instance.
5. **Enterprise SOAR Ticketing Integrations**: Native bi-directional synchronization with enterprise ITSM platforms (ServiceNow, Jira Service Desk, PagerDuty).

---

*End of Product Requirements Document (PRD) & Roadmap — SKYNET MVP.*
