# SKYNET n8n Autonomous Workflow Engine

Orchestration layer connecting ingestion webhooks, AI enrichment nodes, automated mitigation playbooks, and notification channels.

---

## Architecture
1. **Webhook Ingestion:** Ingests metric anomalies and security alerts from FastAPI (`/api/v1/automation`).
2. **AI Enrichment:** Calls LLM / heuristic reasoning engine for root-cause analysis and MITRE mapping.
3. **SOAR Dispatch:** Executes containment playbooks (host isolation, IP blocking) or routes high-risk tasks to the Human-in-the-Loop approval queue.
4. **Master Workflow Definition:** See [workflows/SKYNET_v5_UNIFIED_MASTER_AUTONOMOUS_SOC_PIPELINE.json](../workflows/SKYNET_v5_UNIFIED_MASTER_AUTONOMOUS_SOC_PIPELINE.json).
