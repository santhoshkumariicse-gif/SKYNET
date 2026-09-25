import sqlite3
import bcrypt

con = sqlite3.connect(r'C:\Users\santh\.n8n\database.sqlite')
cur = con.cursor()

# Generate fresh bcrypt hash for 'admin123'
new_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt(10)).decode('utf-8')

cur.execute("UPDATE user SET password = ? WHERE email = ?", (new_hash, 'santhoshkumar160706@gmail.com'))
con.commit()
print("Updated password for santhoshkumar160706@gmail.com to 'admin123'")
con.close()
