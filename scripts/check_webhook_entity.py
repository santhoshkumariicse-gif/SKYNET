import sqlite3

con = sqlite3.connect(r'C:\Users\santh\.n8n\database.sqlite')
cur = con.cursor()

print("webhook_entity rows:", cur.execute("SELECT * FROM webhook_entity").fetchall())
