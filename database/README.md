# SKYNET Database Architecture & Migration Guide

This directory contains the production-grade PostgreSQL DDL schema and migration scripts for the SKYNET AI-Powered Infrastructure Monitoring System.

## Tables Implemented

| Table Name | Purpose | Primary Key | Partitioning / Indexing |
| :--- | :--- | :--- | :--- |
| `devices` | Fleet device registry (PCs, Servers, Android, VMs) | `id (UUID / String)` | `hostname`, `status`, `device_type`, GIN on `tags` |
| `metrics` | High-frequency time-series telemetry (CPU, RAM, GPU, Disk, Net) | `id (UUID)` | `device_id`, `timestamp DESC`, composite `(device_id, timestamp)` |
| `alerts` | Anomaly detections, Sigma rule matches, thermal warnings | `id (UUID)` | `device_id`, `severity`, `status`, `created_at` |
| `incidents`| Correlated attack & infrastructure outage cases | `id (UUID)` | `incident_number`, `severity`, `status` |
| `users` | RBAC users and identity access control | `id (UUID)` | `username`, `role` |

## Migration Execution

To initialize a new PostgreSQL instance:
```bash
psql -U skynet_admin -d skynet_db -f init.sql
```

Using Docker Compose:
```bash
docker-compose -f docker/docker-compose.yml up -d postgres
```
