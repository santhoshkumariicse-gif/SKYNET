import sqlite3
import json

con = sqlite3.connect(r'C:\Users\santh\.n8n\database.sqlite')
cur = con.cursor()

# Get all workflows from workflow_entity
workflows = cur.execute("""
    SELECT id, name, versionId, createdAt, updatedAt, nodes, connections, description, nodeGroups
    FROM workflow_entity
""").fetchall()

print(f"Total workflows in workflow_entity: {len(workflows)}")

existing_history_versions = set(r[0] for r in cur.execute("SELECT versionId FROM workflow_history").fetchall())
print(f"Existing versions in workflow_history: {len(existing_history_versions)}")

inserted_history = 0
for w in workflows:
    wid, name, vid, created_at, updated_at, nodes, conns, desc, node_groups = w
    if vid and vid not in existing_history_versions:
        cur.execute("""
            INSERT INTO workflow_history (
                versionId, workflowId, authors, createdAt, updatedAt, nodes, connections, name, autosaved, description, nodeGroups
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vid, wid, 'KUMAR KUMAR', created_at, updated_at, nodes, conns, name, 0, desc, node_groups or '[]'
        ))
        existing_history_versions.add(vid)
        inserted_history += 1

print(f"Inserted {inserted_history} missing versions into workflow_history.")

# Check workflow_published_version table
pub_cols = [c[1] for c in cur.execute("PRAGMA table_info(workflow_published_version)").fetchall()]
print("workflow_published_version cols:", pub_cols)

# Check webhook_entity table
wh_cols = [c[1] for c in cur.execute("PRAGMA table_info(webhook_entity)").fetchall()]
print("webhook_entity cols:", wh_cols)

con.commit()
con.close()
