# SKYNET POST-MORTEM: Infrastructure Outage INC-2026-0042
**Document ID:** POSTMORTEM-INC-2026-0042  
**Incident Date:** 2026-09-25 (Yesterday)  
**Severity:** CRITICAL DEFCON 1  
**Duration:** 14 minutes (15:22 UTC – 15:36 UTC)  
**Lead Investigator:** SOC Lead Architect Capt. S. Kumar  
**Tags:** outage, incident, postgresql, database, pool-exhaustion, post-mortem  

## Executive Summary
On 2026-09-25 at 15:22 UTC, the SKYNET centralized telemetry ingestion cluster experienced a 14-minute operational degradation where incoming agent telemetry heartbeats received HTTP 503 errors and the dashboard reflected intermittent offline states across 18 endpoints. The root cause was PostgreSQL database connection pool exhaustion triggered by an unclosed async session in the newly deployed analytics worker daemon. Service was fully restored at 15:36 UTC after cycling backend Uvicorn worker pools and applying connection timeouts.

## Root Cause Analysis
1. **Triggering Event:** At 15:18 UTC, an automated batch aggregation job was triggered to compile 24-hour moving baselines for all 48 monitored endpoints.
2. **Defect:** In `app/services/aggregation_service.py`, worker threads failed to release database connections back to the async SQLAlchemy connection pool during exception handling of unreachable edge Android endpoints.
3. **Cascade:** Within 4 minutes, active database connections reached the hard limit of 100 (`max_connections=100`). Subsequent HTTP ingest requests blocked waiting for an available connection until reaching the 30-second gateway timeout.

## Timeline of Events (UTC)
- **15:18:00** — Scheduled cron job kicks off fleet baseline calculation.
- **15:22:15** — First database pool saturation warning flagged by Prometheus alert `PgConnectionPoolSaturated`.
- **15:23:40** — Endpoints began queuing metrics locally in offline ring buffer.
- **15:25:10** — On-call engineer paged; autonomous SOAR playbook `DB_POOL_OVERLOAD_FAILSAFE` attempted connection reset.
- **15:31:00** — Root cause identified in async session generator. Pool size increased from 20 to 100 with connection recycling (`pool_recycle=300`, `pool_timeout=10`).
- **15:36:00** — Backend workers restarted with connection leak patch; all queued agent telemetry drained successfully without data loss.

## Remediation & Permanent Corrective Actions
1. Enforce strict Python context managers (`async with db.begin():`) across all background workers.
2. Implement PgBouncer connection pooling layer in `docker-compose.yml` with transaction pooling mode.
3. Added automated regression integration test `test_database_concurrent_writes_and_rollback` to prevent connection leaks in CI/CD pipeline.
4. Client agents now have durable SQLite local spools to buffer up to 48 hours of telemetry during backend outages.
