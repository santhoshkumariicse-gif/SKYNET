# SKYNET Infrastructure Architecture

Production infrastructure specifications, reverse proxy configs, rate-limiting, and network topologies.

---

## Components
- `nginx/`: High-performance gateway ingress with IP rate limiting and WebSocket proxying.
- Multi-tier network architecture separating frontend, agent ingestion, and persistence data stores.
