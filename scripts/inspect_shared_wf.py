import sqlite3

con = sqlite3.connect(r'C:\Users\santh\.n8n\database.sqlite')
cur = con.cursor()

shared = cur.execute("SELECT * FROM shared_workflow").fetchall()
print("Shared workflow table count:", len(shared))
print("Shared workflow records:", shared)
