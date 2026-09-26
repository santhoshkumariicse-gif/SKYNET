# SKYNET Container Infrastructure

Production-ready Docker orchestration for the full SKYNET ecosystem.

---

## 1. Quick Start

### Build and Launch the Entire Stack
```bash
docker compose -f docker/docker-compose.yml up --build -d
```

### Check Service Health
```bash
docker compose -f docker/docker-compose.yml ps
```

### Stop Services
```bash
docker compose -f docker/docker-compose.yml down
```

---

## 2. Port Map

| Service | Port | Description |
| :--- | :--- | :--- |
| **FastAPI Backend** | `8000` | REST API, OpenAPI Docs (`/docs`), WebSocket (`/ws/live-events`) |
| **Next.js Dashboard** | `3000` | Real-time SOC Web Console |
| **PostgreSQL 15** | `5432` | Relational & Time-Series Database (`skynet_db`) |
| **Redis 7** | `6379` | Fast in-memory caching & session bus |
| **n8n Automation** | `5678` | SOAR & AI Workflow Automation Engine |
