-- ==============================================================================
-- SKYNET v5.0 — Production PostgreSQL Infrastructure Monitoring & XDR Schema
-- Standards: ANSI SQL / PostgreSQL 15+ compatible with B-tree & BRIN indexing
-- ==============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==============================================================================
-- 1. USERS & ACCESS CONTROL TABLE
-- ==============================================================================
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(64) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'SOC_ANALYST',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- ==============================================================================
-- 2. DEVICES / CMDB INVENTORY TABLE
-- ==============================================================================
CREATE TABLE IF NOT EXISTS devices (
    id VARCHAR(64) PRIMARY KEY, -- Agent-supplied UUID or generated identifier
    hostname VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    os_name VARCHAR(100) NOT NULL, -- Windows, Linux, Android, macOS
    os_version VARCHAR(100) NOT NULL,
    device_type VARCHAR(50) NOT NULL DEFAULT 'Workstation', -- Workstation, Laptop, Server, Android, VM
    cpu_cores INT DEFAULT 4,
    total_ram_mb FLOAT DEFAULT 0.0,
    total_disk_gb FLOAT DEFAULT 0.0,
    status VARCHAR(50) NOT NULL DEFAULT 'ONLINE', -- ONLINE, OFFLINE, COMPROMISED, ISOLATED
    agent_version VARCHAR(50) NOT NULL DEFAULT '5.0.0',
    tags JSONB DEFAULT '[]'::jsonb,
    last_seen TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_devices_hostname ON devices(hostname);
CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status);
CREATE INDEX IF NOT EXISTS idx_devices_device_type ON devices(device_type);
CREATE INDEX IF NOT EXISTS idx_devices_last_seen ON devices(last_seen DESC);
CREATE INDEX IF NOT EXISTS idx_devices_tags ON devices USING gin(tags);

-- ==============================================================================
-- 3. TIME-SERIES METRICS TABLE
-- ==============================================================================
CREATE TABLE IF NOT EXISTS metrics (
    id VARCHAR(64) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    device_id VARCHAR(64) NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    cpu FLOAT NOT NULL CHECK (cpu >= 0.0 AND cpu <= 100.0),
    ram FLOAT NOT NULL CHECK (ram >= 0.0 AND ram <= 100.0),
    gpu FLOAT DEFAULT 0.0 CHECK (gpu >= 0.0 AND gpu <= 100.0),
    disk FLOAT NOT NULL CHECK (disk >= 0.0 AND disk <= 100.0),
    network_rx_mb FLOAT DEFAULT 0.0,
    network_tx_mb FLOAT DEFAULT 0.0,
    temperature_c FLOAT DEFAULT 0.0,
    battery_pct FLOAT DEFAULT NULL,
    processes_count INT DEFAULT 0,
    raw_vitals JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_metrics_device_id ON metrics(device_id);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_device_time ON metrics(device_id, timestamp DESC);

-- ==============================================================================
-- 4. ALERTS TABLE
-- ==============================================================================
CREATE TABLE IF NOT EXISTS alerts (
    id VARCHAR(64) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    device_id VARCHAR(64) REFERENCES devices(id) ON DELETE SET NULL,
    alert_type VARCHAR(64) NOT NULL DEFAULT 'High CPU', -- High CPU, High RAM, High GPU, Disk Critical, Device Offline
    severity VARCHAR(32) NOT NULL DEFAULT 'Warning', -- Info, Warning, Critical
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    source VARCHAR(64) NOT NULL DEFAULT 'ANOMALY_ENGINE', -- SIGMA_RULE, ANOMALY_ENGINE, THREAT_INTEL
    status VARCHAR(32) NOT NULL DEFAULT 'NEW', -- NEW, ACKNOWLEDGED, RESOLVED, SUPPRESSED
    acknowledged BOOLEAN NOT NULL DEFAULT FALSE,
    host_name VARCHAR(255),
    host_ip VARCHAR(45),
    mitre_technique VARCHAR(32),
    threat_score INT DEFAULT 50 CHECK (threat_score >= 0 AND threat_score <= 100),
    event_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alerts_device_id ON alerts(device_id);
CREATE INDEX IF NOT EXISTS idx_alerts_alert_type ON alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(acknowledged);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC);

-- ==============================================================================
-- 5. INCIDENTS TABLE
-- ==============================================================================
CREATE TABLE IF NOT EXISTS incidents (
    id VARCHAR(64) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    incident_number VARCHAR(32) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(32) NOT NULL DEFAULT 'HIGH',
    status VARCHAR(32) NOT NULL DEFAULT 'NEW', -- NEW, TRIAGED, INVESTIGATING, CONTAINED, CLOSED
    defcon_level INT DEFAULT 3 CHECK (defcon_level >= 1 AND defcon_level <= 5),
    confidence_score FLOAT DEFAULT 0.85,
    lead_commander VARCHAR(100) DEFAULT 'SKYNET Autonomous AI',
    root_cause TEXT,
    summary TEXT,
    recommended_actions JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_incidents_number ON incidents(incident_number);
CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_created_at ON incidents(created_at DESC);

-- ==============================================================================
-- 6. DEVICE BASELINES (Rolling statistical models for anomaly detection)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS baselines (
    id VARCHAR(64) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    device_id VARCHAR(64) UNIQUE NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    avg_cpu FLOAT DEFAULT 25.0,
    std_cpu FLOAT DEFAULT 8.0,
    avg_ram FLOAT DEFAULT 45.0,
    std_ram FLOAT DEFAULT 6.0,
    avg_gpu FLOAT DEFAULT 10.0,
    std_gpu FLOAT DEFAULT 5.0,
    avg_disk FLOAT DEFAULT 40.0,
    std_disk FLOAT DEFAULT 2.0,
    avg_network FLOAT DEFAULT 1.5,
    std_network FLOAT DEFAULT 1.0,
    sample_count INT DEFAULT 100,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_baselines_device_id ON baselines(device_id);

-- ==============================================================================
-- 7. ANOMALIES (Detected behavioural deviations & intelligence records)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS anomalies (
    id VARCHAR(64) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    device_id VARCHAR(64) NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    anomaly_type VARCHAR(64) NOT NULL, -- CPU_SPIKE, MEMORY_LEAK, DISK_PRESSURE, NETWORK_SURGE, UNUSUAL_INACTIVITY
    anomaly_score FLOAT NOT NULL CHECK (anomaly_score >= 0.0 AND anomaly_score <= 100.0),
    confidence FLOAT NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
    reason TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, INVESTIGATING, RESOLVED, FALSE_POSITIVE
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_anomalies_device_id ON anomalies(device_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_type ON anomalies(anomaly_type);
CREATE INDEX IF NOT EXISTS idx_anomalies_score ON anomalies(anomaly_score DESC);
CREATE INDEX IF NOT EXISTS idx_anomalies_created_at ON anomalies(created_at DESC);

-- ==============================================================================
-- AUTOMATIC TIMESTAMP UPDATE TRIGGER FUNCTION
-- ==============================================================================
CREATE OR REPLACE FUNCTION update_timestamp_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trg_devices_updated_at BEFORE UPDATE ON devices FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();
CREATE TRIGGER trg_alerts_updated_at BEFORE UPDATE ON alerts FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();
CREATE TRIGGER trg_incidents_updated_at BEFORE UPDATE ON incidents FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();
CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();
CREATE TRIGGER trg_baselines_updated_at BEFORE UPDATE ON baselines FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();
