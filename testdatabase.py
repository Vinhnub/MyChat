import sqlite3
from datetime import datetime

# Kết nối database
conn = sqlite3.connect("Database/chat.db")
cur = conn.cursor()

# === Thêm dữ liệu GroupChat ===


# Lấy groupID vừa tạo để dùng cho MemberOf
cur.execute("delete from User")

conn.commit()

# Kiểm tra dữ liệu

conn.close()
