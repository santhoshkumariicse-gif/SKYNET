import sqlite3
import json

con = sqlite3.connect(r'C:\Users\santh\.n8n\database.sqlite')
cur = con.cursor()

row_entity = cur.execute("SELECT versionId, activeVersionId FROM workflow_entity WHERE id='Gqz8Ke2syWjGWL0u'").fetchone()
print("workflow_entity:", row_entity)

row_pub = cur.execute("SELECT * FROM workflow_published_version WHERE workflowId='Gqz8Ke2syWjGWL0u'").fetchone()
print("workflow_published_version:", row_pub)

row_hist = cur.execute("SELECT versionId, workflowId, name, length(nodes) FROM workflow_history WHERE workflowId='Gqz8Ke2syWjGWL0u'").fetchall()
print("workflow_history:", row_hist)
