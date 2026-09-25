# SKYNET v5 — 3 Top-Level n8n Workflows

1. SKYNET CORE — Detection & Intelligence
2. SKYNET SOC — Investigation & Incident Operations
3. SKYNET SOAR — Response & Autonomous Operations

Import the three JSON files into n8n.

Important:
- These are top-level orchestration/scaffold workflows, not a production SOC by themselves.
- External SIEM/log sources, EDR, IAM, firewall, TI providers, AI model, database, ticketing, and approval systems must be connected and credentialed.
- High-impact response actions are approval-gated by default.
- Connector/action nodes are placeholders so the workflows can be safely imported before production credentials are configured.
- The 150 previously defined capabilities are intended to live as internal branches/subflows inside these three domains rather than as 150 independent top-level workflows.
