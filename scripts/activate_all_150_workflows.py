import sqlite3
import json

con = sqlite3.connect(r'C:\Users\santh\.n8n\database.sqlite')
cur = con.cursor()

# Get all workflows
workflows = cur.execute("""
    SELECT id, name, versionId, createdAt, updatedAt, nodes
    FROM workflow_entity
""").fetchall()

print(f"Total workflows in database: {len(workflows)}")

activated_count = 0
registered_webhooks = 0

for w in workflows:
    wid, name, vid, cat, uat, nodes_json = w
    if not vid:
        continue
    
    # 1. Set active in workflow_entity
    cur.execute("UPDATE workflow_entity SET active = 1, activeVersionId = ? WHERE id = ?", (vid, wid))
    
    # 2. Insert into workflow_published_version
    cur.execute("""
        INSERT OR REPLACE INTO workflow_published_version (workflowId, publishedVersionId, createdAt, updatedAt)
        VALUES (?, ?, ?, ?)
    """, (wid, vid, cat, uat))
    activated_count += 1
    
    # 3. Check for webhook nodes
    if nodes_json:
        try:
            nodes = json.loads(nodes_json)
            for n in nodes:
                if n.get('type') == 'n8n-nodes-base.webhook':
                    params = n.get('parameters', {})
                    path = params.get('path')
                    method = params.get('httpMethod', 'POST').upper()
                    node_name = n.get('name', 'Webhook')
                    webhook_id = n.get('webhookId', n.get('id'))
                    
                    if path:
                        cur.execute("""
                            INSERT OR REPLACE INTO webhook_entity (workflowId, webhookPath, method, node, webhookId, pathLength)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (wid, path, method, node_name, webhook_id, len(path)))
                        registered_webhooks += 1
        except Exception as e:
            print(f"Error parsing nodes for {name}: {e}")

con.commit()
print(f"Successfully activated {activated_count} workflows.")
print(f"Successfully registered {registered_webhooks} active webhooks in n8n database.")

# Verify counts
total_active = cur.execute("SELECT count(*) FROM workflow_entity WHERE active = 1").fetchone()[0]
total_webhooks = cur.execute("SELECT count(*) FROM webhook_entity").fetchone()[0]
print(f"Verification: {total_active} active workflows, {total_webhooks} webhooks registered in database.")
con.close()
