import sqlite3

conn = sqlite3.connect("Database/chat.db")
cur = conn.cursor()
cur.execute("select * from User")
print("=========== User ===========")
for row in cur.fetchall():
    print(row)

cur.execute("select * from GroupChat")
print("=========== GroupChat ===========")
for row in cur.fetchall():
    print(row)

cur.execute("select * from MemberOf")
print("=========== MemberOf ===========")
for row in cur.fetchall():
    print(row)

cur.execute("select * from Message")
print("=========== Message ===========")
for row in cur.fetchall():
    print(row)


# cur.execute("delete from GroupChat")
# conn.commit()

users = [
    ("vinh", "Nguyễn Văn Vĩnh", "hash123"),
    ("duc", "Nguyễn Văn Dục", "hash456"),
    ("hoa", "Trần Thị Hoa", "hash789"),
]

groups = [
    ("pythonDev", "1234", "Nhóm học Python", "vinh"),
    ("gamers", "5678", "Team chơi game", "hoa"),
]

messages = [
    ("Xin chào mọi người!", "2025/08/27 09:00", "vinh", "pythonDev"),
    ("Hello Vinh", "2025/08/27 09:05", "hoa", "pythonDev"),
    ("Hôm nay chơi Liên Minh?", "2025/08/27 10:00", "hoa", "gamers"),
    ("Ok luôn nè", "2025/08/27 10:10", "duc", "gamers"),
]

members = [
    ("vinh", "pythonDev"),
    ("hoa", "pythonDev"),
    ("duc", "gamers"),
    ("hoa", "gamers"),
]

# Insert data
# cur.executemany("INSERT OR IGNORE INTO User VALUES (?, ?, ?)", users)
# cur.executemany("INSERT OR IGNORE INTO GroupChat VALUES (?, ?, ?, ?)", groups)
# cur.executemany("INSERT OR IGNORE INTO Message(mesContent, date, userName, groupName) VALUES (?, ?, ?, ?)", messages)
# cur.executemany("INSERT OR IGNORE INTO MemberOf VALUES (?, ?)", members)

# conn.commit()

conn.close()

