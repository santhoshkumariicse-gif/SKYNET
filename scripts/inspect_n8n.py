import sqlite3

con = sqlite3.connect(r'C:\Users\santh\.n8n\database.sqlite')
cur = con.cursor()

user_cols = [c[1] for c in cur.execute("PRAGMA table_info(user)").fetchall()]
print("User cols:", user_cols)

users = cur.execute(f"SELECT email, firstName, lastName FROM user").fetchall()
print("Registered Users:", users)

wf_count = cur.execute("SELECT count(*) FROM workflow_entity").fetchone()[0]
print("Workflows in n8n database:", wf_count)

if wf_count > 0:
    wf_sample = cur.execute("SELECT id, name, active FROM workflow_entity LIMIT 10").fetchall()
    print("Workflows sample:", wf_sample)

projects = cur.execute("SELECT id, name, type FROM project").fetchall()
print("Projects:", projects)
