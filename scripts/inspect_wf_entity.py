import sqlite3

con = sqlite3.connect(r'C:\Users\santh\.n8n\database.sqlite')
cur = con.cursor()

wf_cols = [c[1] for c in cur.execute("PRAGMA table_info(workflow_entity)").fetchall()]
print("Workflow entity cols:", wf_cols)

sample = cur.execute("SELECT id, name, active, nodes, connections FROM workflow_entity LIMIT 1").fetchone()
print("Sample ID:", sample[0])
print("Sample Name:", sample[1])
print("Nodes type/len:", type(sample[3]), len(sample[3]) if sample[3] else 0)
