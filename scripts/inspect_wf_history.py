import sqlite3

con = sqlite3.connect(r'C:\Users\santh\.n8n\database.sqlite')
cur = con.cursor()

cols = [c[1] for c in cur.execute("PRAGMA table_info(workflow_history)").fetchall()]
print("workflow_history cols:", cols)

sample = cur.execute("SELECT * FROM workflow_history LIMIT 1").fetchone()
print("Sample history row:", sample)
