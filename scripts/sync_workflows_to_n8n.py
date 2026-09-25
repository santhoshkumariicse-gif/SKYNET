import sqlite3
import json
import os
import shutil
import uuid
from datetime import datetime

n8n_dir = r'C:\Users\santh\.n8n'
db_path = os.path.join(n8n_dir, 'database.sqlite')
backup_path = os.path.join(n8n_dir, 'database.sqlite.bak')

if not os.path.exists(backup_path):
    shutil.copy2(db_path, backup_path)
    print(f"Created backup at {backup_path}")

con = sqlite3.connect(db_path)
cur = con.cursor()

# Get existing workflow names and IDs
existing_wfs = {name: wid for wid, name in cur.execute("SELECT id, name FROM workflow_entity").fetchall()}
print(f"Existing workflows in n8n: {len(existing_wfs)}")

# Get personal project ID
project_row = cur.execute("SELECT id FROM project WHERE type='personal' LIMIT 1").fetchone()
if not project_row:
    project_row = cur.execute("SELECT id FROM project LIMIT 1").fetchone()
project_id = project_row[0] if project_row else 'YIUgtOzBOXBy7Csq'
print(f"Target project ID: {project_id}")

base_dir = os.path.dirname(os.path.dirname(__file__))

def generate_id():
    import random
    import string
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(16))

# 1. Sync Master Orchestrator
master_path = os.path.join(base_dir, 'workflows', 'SKYNET_v5_MASTER_ORCHESTRATOR.json')
with open(master_path, 'r', encoding='utf-8') as f:
    master_json = json.load(f)

master_name = master_json.get('name', 'SKYNET v5 - MASTER ORCHESTRATOR')
now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

if master_name not in existing_wfs:
    wf_id = generate_id()
    cur.execute("""
        INSERT INTO workflow_entity (
            id, name, active, nodes, connections, settings, staticData, pinData,
            versionId, triggerCount, meta, parentFolderId, createdAt, updatedAt,
            isArchived, versionCounter, description, activeVersionId, nodeGroups, sourceWorkflowId
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        wf_id, master_name, 0,
        json.dumps(master_json.get('nodes', [])),
        json.dumps(master_json.get('connections', {})),
        json.dumps(master_json.get('settings', {"executionOrder": "v1", "binaryMode": "separate"})),
        None, json.dumps({}),
        str(uuid.uuid4()), 0, None, None, now, now, 0, 1,
        "Master Orchestrator coordinating all 15 SKYNET v5.0 security domains",
        None, json.dumps([]), None
    ))
    
    cur.execute("""
        INSERT INTO shared_workflow (workflowId, projectId, role, createdAt, updatedAt)
        VALUES (?, ?, ?, ?, ?)
    """, (wf_id, project_id, 'workflow:owner', now, now))
    
    print(f"Inserted Master Orchestrator: {wf_id}")
else:
    print(f"Master Orchestrator already present with ID: {existing_wfs[master_name]}")

# 2. Sync all 150 workflows
wf_150_dir = os.path.join(base_dir, 'workflows', 'SKYNET_v5_ALL_150_N8N_WORKFLOWS')
wf_files = sorted([f for f in os.listdir(wf_150_dir) if f.startswith('SKYNET_v5_WF') and f.endswith('.json')])

inserted_count = 0
for f in wf_files:
    fpath = os.path.join(wf_150_dir, f)
    with open(fpath, 'r', encoding='utf-8') as fp:
        try:
            wdata = json.load(fp)
            name = wdata.get('name')
            if not name:
                continue
            
            # Check if workflow with exact name or partial name already exists
            if name not in existing_wfs:
                wf_id = generate_id()
                cur.execute("""
                    INSERT INTO workflow_entity (
                        id, name, active, nodes, connections, settings, staticData, pinData,
                        versionId, triggerCount, meta, parentFolderId, createdAt, updatedAt,
                        isArchived, versionCounter, description, activeVersionId, nodeGroups, sourceWorkflowId
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    wf_id, name, 0,
                    json.dumps(wdata.get('nodes', [])),
                    json.dumps(wdata.get('connections', {})),
                    json.dumps(wdata.get('settings', {"executionOrder": "v1", "binaryMode": "separate"})),
                    None, json.dumps({}),
                    str(uuid.uuid4()), 0, None, None, now, now, 0, 1,
                    f"SKYNET v5.0 Playbook: {name}",
                    None, json.dumps([]), None
                ))
                
                cur.execute("""
                    INSERT INTO shared_workflow (workflowId, projectId, role, createdAt, updatedAt)
                    VALUES (?, ?, ?, ?, ?)
                """, (wf_id, project_id, 'workflow:owner', now, now))
                
                existing_wfs[name] = wf_id
                inserted_count += 1
        except Exception as e:
            print(f"Error on {f}: {e}")

con.commit()
total_now = cur.execute("SELECT count(*) FROM workflow_entity").fetchone()[0]
print(f"Inserted {inserted_count} new workflows.")
print(f"Total workflows in n8n database now: {total_now}")
con.close()
