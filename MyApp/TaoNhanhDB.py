import sqlite3

# Tạo file và kết nối
conn = sqlite3.connect("mydatabase.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM useraccount")
for row in cursor.fetchall():
    print(row)

