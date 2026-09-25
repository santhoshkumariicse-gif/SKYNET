import sqlite3

con = sqlite3.connect(r'C:\Users\santh\.n8n\database.sqlite')
cur = con.cursor()
row = cur.execute("SELECT id, email, firstName, lastName, password FROM user").fetchone()
print("User ID:", row[0])
print("Email:", row[1])
print("Name:", row[2], row[3])
print("Password hash prefix:", row[4][:15] if row[4] else "NO PASSWORD")
