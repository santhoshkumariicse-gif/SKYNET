import sqlite3

con = sqlite3.connect(r'C:\Users\santh\.n8n\database.sqlite')
cur = con.cursor()

print("Current published workflows:", cur.execute("SELECT * FROM workflow_published_version").fetchall())
print("Current registered webhooks:", cur.execute("SELECT * FROM webhook_entity").fetchall())

# Find Master Orchestrator workflow ID and version ID
row = cur.execute("SELECT id, versionId, createdAt, updatedAt FROM workflow_entity WHERE name = 'SKYNET v5 - MASTER ORCHESTRATOR'").fetchone()
if row:
    wid, vid, cat, uat = row
    print("Master Orchestrator:", wid, vid)
    
    # Insert or replace into workflow_published_version
    cur.execute("""
        INSERT OR REPLACE INTO workflow_published_version (workflowId, publishedVersionId, createdAt, updatedAt)
        VALUES (?, ?, ?, ?)
    """, (wid, vid, cat, uat))
    
    # Also update active = 1 in workflow_entity
    cur.execute("UPDATE workflow_entity SET active = 1, activeVersionId = ? WHERE id = ?", (vid, wid))
    
    # Register production webhook in webhook_entity
    # path: 'skynet/v5/orchestrator', method: 'POST', node: 'Master Security Event Webhook', webhookId: 'master-webhook-intake'
    cur.execute("""
        INSERT OR REPLACE INTO webhook_entity (workflowId, webhookPath, method, node, webhookId, pathLength)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (wid, 'skynet/v5/orchestrator', 'POST', 'Master Security Event Webhook', 'master-webhook-intake', len('skynet/v5/orchestrator')))

con.commit()
print("Updated published version and registered webhook for Master Orchestrator!")
con.close()
