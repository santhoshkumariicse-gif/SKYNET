import sqlite3
import json

con = sqlite3.connect(r'C:\Users\santh\.n8n\database.sqlite')
con.row_factory = sqlite3.Row
cur = con.cursor()

row = cur.execute("SELECT * FROM workflow_entity WHERE id='Cq5KJ7C3CAYnuMnH'").fetchone()
for k in row.keys():
    v = row[k]
    if isinstance(v, str) and len(v) > 60:
        print(f"{k}: str of length {len(v)}")
    else:
        print(f"{k}: {v}")
