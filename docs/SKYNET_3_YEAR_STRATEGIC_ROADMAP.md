# SKYNET — 3-Year Strategic Engineering & Product Roadmap (2026–2029)

**Author:** Chief Technology Officer, Product Strategist & Platform Architect  
**Operating Constraints:** Lean core engineering team (4–6 engineers), bootstrapped/seed budget, open-source-first foundation (Ollama, PostgreSQL, TimescaleDB, Qdrant, Nginx, Next.js).

---

## 1. Strategic Principles & Vision

1. **Pragmatic Automation over Vaporware**: Prioritize deterministic, testable, explainable engineering over opaque black-box systems.
2. **Air-Gapped & Sovereign AI**: Maintain 100% on-premises execution capability. Zero dependency on proprietary third-party cloud LLM APIs.
3. **Open-Source Core, Enterprise Fabric**: Build upon battle-tested open-source primitives to ensure vendor neutrality and low capital expenditure.

---

## 2. Year 1 (2026–2027): Foundation, AI Analytics, Hardening & Initial Scale

### Objectives
Establish a rock-solid, production-grade core monitoring and local AI analytics engine capable of monitoring 1,000–5,000 nodes with sub-5ms API latency and zero cloud data egress.

### Quarterly Deliverables
- **Q1 2026 (Completed): Foundation & Fleet Visibility**
  - High-throughput FastAPI telemetry gateway with TimescaleDB hypertables.
  - Windows background agent and Android native Kotlin telemetry collector.
  - Next.js 14 SOC command center with real-time Recharts and dual light/dark themes.
- **Q2 2026 (Completed): Explainable AI & Local RAG Engine**
  - Multi-factor behavioral Health Scoring (0–100) and Gaussian rolling baselines.
  - Local Vector Store with normalized cosine similarity search (`p50 < 10ms`).
  - Strict anti-hallucination guardrails and source citation engine.
- **Q3 2026 (Completed): Security Hardening & Observability Fabric**
  - JWT access/refresh token lifecycle with Argon2id password hashing.
  - Cryptographic device identity with hardware fingerprinting and HMAC replay protection.
  - OpenTelemetry W3C trace propagation and Prometheus exposition (`/metrics`).
- **Q4 2026: Multi-Site Federation & Production Pilots**
  - Multi-site geographic hierarchy (Headquarters, Data Centers, Regional Branches).
  - Cross-site health and risk benchmarking matrix.
  - 3 enterprise pilot deployments with SOC 2 compliance readiness audit.

### Year 1 Strategic Analysis
- **Dependencies:** Stable Ollama / Llama 3.2 local runtimes, PostgreSQL 16 TimescaleDB extension.
- **Risks:** Memory constraints on low-spec edge servers running local LLM inference.
- **Mitigating Controls:** Hybrid deterministic fallback in `RAGEngine` ensuring instant answers without GPU dependencies.
- **Success Metrics:**
  - Ingestion throughput $\ge 250$ batches/sec per worker.
  - Zero critical security vulnerabilities in static code scanning (Bandit clean).
  - 100% automated test pass rate across 45+ test cases.

---

## 3. Year 2 (2027–2028): Enterprise Multi-Tenancy, SOAR & Wazuh Fabric

### Objectives
Transition SKYNET from a single-tenant operations tool into a multi-tenant Managed Service Provider (MSP) and enterprise-scale platform monitoring 25,000+ nodes.

### Quarterly Deliverables
- **Q1 2027: Multi-Tenant Tenant Isolation & RBAC Extension**
  - Row-Level Security (RLS) in PostgreSQL with tenant schema segregation.
  - Self-service organization onboarding with custom SAML 2.0 / Okta SSO integration.
- **Q2 2027: Distributed Autonomous SOAR Playbooks**
  - Visual no-code playbook editor integrating with n8n and Python scripts.
  - Safe automated rollbacks for incident containment actions.
  - Integration with ServiceNow and PagerDuty bi-directional sync.
- **Q3 2027: Wazuh EDR & SIEM Deep Ingestion Fabric**
  - Distributed Wazuh manager cluster ingestion pipeline.
  - Unified vulnerability scoring combining CVE impact with live metric saturation.
  - MITRE ATT&CK automated correlation across 62 SOC procedures.
- **Q4 2027: Mobile Fleet Management (MDM Integration)**
  - Remote Android agent update distribution and battery saver heuristics.
  - Zero-touch device enrollment via QR-code provisioning.

### Year 2 Strategic Analysis
- **Dependencies:** Redis cluster for cross-tenant pub/sub queuing; Kubernetes multi-pod ingress controllers.
- **Risks:** Tenant noisy-neighbor performance degradation.
- **Mitigating Controls:** Strict per-tenant rate-limiting token buckets and database connection pooling.
- **Success Metrics:**
  - 15 paying enterprise/MSP pilot customers.
  - 99.95% API uptime SLA across multi-tenant clusters.
  - Sub-30 second MTTR on automated SOAR containment scenarios.

---

## 4. Year 3 (2028–2029): Autonomous Operations & Predictive Self-Healing

### Objectives
Deliver the ultimate vision of SKYNET: an autonomous, self-healing infrastructure mesh that predicts failures before they manifest and dynamically re-allocates workloads with zero human intervention.

### Quarterly Deliverables
- **Q1 2028: eBPF Kernel Mesh (Linux Containers)**
  - Kernel-level low-overhead network and syscall observability using eBPF probes.
  - Zero-agent microservice tracing for Kubernetes pods.
- **Q2 2028: Predictive Failure Intelligence**
  - Time-series transformer models predicting disk exhaustion and memory leaks 72 hours in advance.
  - Automated ticket pre-generation with prescriptive remediation steps.
- **Q3 2028: Autonomous Closed-Loop Self-Healing**
  - Dynamic autoscaling and pod rescheduling triggered by AI anomaly forecasts.
  - Automated canary deployment verification and rollbacks.
- **Q4 2028: Global Fleet Federation & Marketplace**
  - Community Sigma detection rule and SOAR playbook marketplace.
  - Encrypted peer-to-peer telemetry federation for distributed edge nodes.

### Year 3 Strategic Analysis
- **Dependencies:** Stable eBPF Linux kernel support (v5.15+), mature lightweight time-series transformers.
- **Risks:** Over-eager autonomous actions causing service disruption.
- **Mitigating Controls:** Mandatory Human-in-the-Loop approval policies (`backend/app/models/models.py`) with customizable confidence thresholds before autonomous destructive actions.
- **Success Metrics:**
  - 70% of infrastructure incidents resolved autonomously without human on-call paging.
  - Mean Time to Detect (MTTD) $< 5$ seconds.
  - $1.5M+ Annual Recurring Revenue (ARR).

---

## 5. Budget, Resource & Team Allocation Model

```
+-----------------------------------------------------------------------------------+
|                        3-YEAR LEAN RESOURCE ALLOCATION                            |
+-----------------------------------------------------------------------------------+
| Phase    | Team Headcount                   | Infrastructure & Tooling Budget     |
+----------+----------------------------------+-------------------------------------+
| Year 1   | 4 Engineers (2 Fullstack,        | $18,000/yr                          |
|          | 1 AI/Backend, 1 SRE/DevOps)      | (Hetzner Bare Metal, CI/CD, Domain) |
+----------+----------------------------------+-------------------------------------+
| Year 2   | 6 Engineers (+1 Security,        | $45,000/yr                          |
|          | +1 Mobile/Kernel)                | (Multi-region cloud runners, Qdrant)|
+----------+----------------------------------+-------------------------------------+
| Year 3   | 9 Engineers (+2 ML Research,     | $95,000/yr                          |
|          | +1 Customer Solutions)           | (GPU inference clusters, SOC 2 Type 2)|
+-----------------------------------------------------------------------------------+
```
