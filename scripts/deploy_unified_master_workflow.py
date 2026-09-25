import sqlite3
import json
import os
import uuid
from datetime import datetime

n8n_db = r'C:\Users\santh\.n8n\database.sqlite'
con = sqlite3.connect(n8n_db)
cur = con.cursor()

# 1. Clean up old fragmented workflows so n8n is clean and operator-focused
print("Cleaning up old fragmented workflow cards from n8n database...")
cur.execute("DELETE FROM workflow_entity WHERE name LIKE 'SKYNET v5 - WF%'")
cur.execute("DELETE FROM workflow_history WHERE name LIKE 'SKYNET v5 - WF%'")
cur.execute("DELETE FROM webhook_entity WHERE webhookPath LIKE 'skynet/v5/wf-%'")

# 2. Load the Unified Master Workflow
unified_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'workflows', 'SKYNET_v5_UNIFIED_MASTER_AUTONOMOUS_SOC_PIPELINE.json')
with open(unified_path, 'r', encoding='utf-8') as f:
    unified_data = json.load(f)

wf_name = unified_data.get('name')
wf_id = 'SKYNET00UNIFIED1'
version_id = str(uuid.uuid4())
now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

# Get personal project ID
project_row = cur.execute("SELECT id FROM project WHERE type='personal' LIMIT 1").fetchone()
project_id = project_row[0] if project_row else 'YIUgtOzBOXBy7Csq'

# Delete any existing unified workflow
cur.execute("DELETE FROM workflow_entity WHERE id = ? OR name = ?", (wf_id, wf_name))
cur.execute("DELETE FROM workflow_history WHERE workflowId = ?", (wf_id,))
cur.execute("DELETE FROM webhook_entity WHERE workflowId = ?", (wf_id,))

# Insert into workflow_entity
cur.execute("""
    INSERT INTO workflow_entity (
        id, name, active, nodes, connections, settings, staticData, pinData,
        versionId, triggerCount, meta, parentFolderId, createdAt, updatedAt,
        isArchived, versionCounter, description, activeVersionId, nodeGroups, sourceWorkflowId
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    wf_id, wf_name, 1,
    json.dumps(unified_data.get('nodes', [])),
    json.dumps(unified_data.get('connections', {})),
    json.dumps(unified_data.get('settings', {"executionOrder": "v1", "binaryMode": "separate"})),
    None, json.dumps({}),
    version_id, 1, None, None, now, now, 0, 1,
    "Unified Master Autonomous SOC Pipeline: Ingestion -> OCSF Normalization -> Enrichment -> TIP -> Sigma Detection -> Temporal Correlation -> Risk Scoring -> Alerting -> Investigation -> SOAR Defense & Human Gating -> HMAC Audit",
    version_id, json.dumps([]), None
))

# Insert into workflow_history
cur.execute("""
    INSERT INTO workflow_history (
        versionId, workflowId, authors, createdAt, updatedAt, nodes, connections, name, autosaved, description, nodeGroups
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    version_id, wf_id, 'KUMAR KUMAR', now, now,
    json.dumps(unified_data.get('nodes', [])),
    json.dumps(unified_data.get('connections', {})),
    wf_name, 0,
    "Production Release v5.0",
    json.dumps([])
))

# Insert into workflow_published_version
cur.execute("""
    INSERT OR REPLACE INTO workflow_published_version (workflowId, publishedVersionId, createdAt, updatedAt)
    VALUES (?, ?, ?, ?)
""", (wf_id, version_id, now, now))

# Insert into shared_workflow
cur.execute("""
    INSERT OR REPLACE INTO shared_workflow (workflowId, projectId, role, createdAt, updatedAt)
    VALUES (?, ?, ?, ?, ?)
""", (wf_id, project_id, 'workflow:owner', now, now))

# Register production webhook
cur.execute("""
    INSERT OR REPLACE INTO webhook_entity (workflowId, webhookPath, method, node, webhookId, pathLength)
    VALUES (?, ?, ?, ?, ?, ?)
""", (wf_id, 'skynet/v5/unified-soc', 'POST', '01 Ingestion Webhook Trigger', 'unified-webhook-trigger', len('skynet/v5/unified-soc')))

con.commit()

remaining_wfs = cur.execute("SELECT id, name, active FROM workflow_entity").fetchall()
print(f"\nSuccessfully deployed Unified Master Workflow!")
print(f"Total Workflows in n8n now: {len(remaining_wfs)}")
for wid, wname, wact in remaining_wfs:
    print(f"  - [{wid}] {wname} (Active: {wact})")

con.close()
