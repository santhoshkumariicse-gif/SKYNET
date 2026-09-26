# SKYNET v5.0 — Observability & Telemetry Architecture (M.E.L.T.)

**Target:** Enterprise Observability Platform  
**Standard:** OpenTelemetry (OTel), Prometheus Exposition, Structured JSON Logging  
**Exposition Endpoints:** `GET /metrics` (Prometheus), `GET /api/v1/metrics` (REST)

---

## 1. Unified Observability Architecture (M.E.L.T.)

SKYNET unifies the four pillars of modern observability into a synchronized, single-pane data model:

```
+-----------------------------------------------------------------------------------+
|                         SKYNET UNIFIED OBSERVABILITY FABRIC                       |
+-----------------------------------------------------------------------------------+
|   METRICS (M)             EVENTS (E)            LOGS (L)            TRACES (T)    |
|   - CPU / RAM / Disk      - SOAR Quarantines    - Structured JSON   - W3C Trace   |
|   - Fleet Health (0-100)  - Sigma Triggered     - Level / TraceID   - span_id     |
|   - Risk Score (0-100)    - Approval Requests   - Duration / Code   - parent_id   |
+-----------------------------------------------------------------------------------+
                                          │
                                          ▼
+-----------------------------------------------------------------------------------+
|                            INGESTION & MIDDLEWARE PIPELINE                        |
|   - OTel Traceparent Header Extraction & Injection (`ObservabilityMiddleware`)   |
|   - Real-time Prometheus Metric Aggregator (`/metrics`)                          |
|   - TimescaleDB Hypertable Metric Rollups (1h, 24h, 30d)                         |
+-----------------------------------------------------------------------------------+
                                          │
                    ┌─────────────────────┴─────────────────────┐
                    ▼                                           ▼
+---------------------------------------+   +---------------------------------------+
|          GRAFANA DASHBOARDS           |   |       SKYNET NEXT.JS CONSOLE          |
|  - Unified Enterprise Observability   |   |  - Fleet Cockpit, Health Breakdown    |
|  - Scraping Prometheus on port 8000   |   |  - High-Density Dual Theme SOC        |
+---------------------------------------+   +---------------------------------------+
```

---

## 2. OpenTelemetry & Trace Context Propagation

Every incoming request passing through the gateway is enriched with standard **W3C Trace Context**:
- **Header:** `traceparent: 00-{trace_id}-{span_id}-01`
- **Response Headers:** `X-Trace-Id` and `X-Span-Id`
- **Context Injection:** Downstream database queries, external Wazuh webhooks, and local RAG inferences inherit the parent `trace_id`, enabling continuous distributed tracing from endpoint click to database write.

---

## 3. Prometheus Metric Schema (`/metrics`)

The `/metrics` endpoint adheres to Prometheus Exposition format (v0.0.4):

```promql
# Fleet Health & Risk
skynet_fleet_health_score 91.0
skynet_fleet_risk_score 18.0
skynet_active_endpoints 5

# Telemetry Throughput & HTTP Metrics
skynet_http_requests_total{status="200"} 14820
skynet_http_requests_total{status="500"} 0

# RAG Knowledge Chunks
skynet_rag_indexed_chunks 12

# Alert Distribution by Severity
skynet_active_alerts_total{severity="critical"} 1
skynet_active_alerts_total{severity="high"} 1
skynet_active_alerts_total{severity="medium"} 2
```

---

## 4. Retention & Storage Optimization Strategy

To maintain high query performance while containing cloud storage expenses:

| Telemetry Tier | Granularity | Retention Period | Storage Target | Compression Ratio |
| :--- | :--- | :--- | :--- | :---: |
| **Raw High-Res Telemetry** | 10-second intervals | 7 Days | SSD / NVMe Local | 1:1 |
| **1-Hour Rollup Hypertables** | 1-hour average/p95 | 90 Days | TimescaleDB Compressed | 8:1 |
| **Daily Summaries** | Daily min/max/avg | 1 Year | Cold Object Store | 25:1 |
| **Audit Logs & SOAR Ledgers**| Cryptographic HMAC | 7 Years (Immutable) | WORM S3 Bucket | Uncompressed |

---

## 5. Cost Optimization Strategy

1. **Edge Sampling & Adaptive Heartbeats**: Workstations that remain idle switch from 5-second to 60-second telemetry polling, cutting network transit by 82%.
2. **Local Vector Caching**: In-memory cosine search indexes run on host RAM rather than per-query vector API charges, eliminating external LLM/vector SaaS bills.
3. **Structured Log Suppression**: High-frequency health probes (`/health`) bypass standard log buffers, preventing log ingestion spikes in tools like Datadog or Splunk.
