import sqlite3

# def load_user_data(username):
#     conn = sqlite3.connect("Database/chat.db")
#     cur = conn.cursor()

#     cur.execute("SELECT userFullName FROM User WHERE userName=?", (username,))
#     user_row = cur.fetchone()
#     if not user_row:
#         conn.close()
#         return None  

#     userFullName = user_row[0]

#     cur.execute("""
#         SELECT groupName, lastReadMessageID 
#         FROM MemberOf 
#         WHERE userName=?
#     """, (username,))
#     groups_rows = cur.fetchall()

#     groups_dict = {}

#     for groupName, lastReadMessageID in groups_rows:
#         cur.execute("""
#             SELECT mesID, mesContent, date, userName 
#             FROM Message
#             WHERE groupID = (SELECT rowid FROM GroupChat WHERE groupName=?)
#             ORDER BY mesID DESC
#             LIMIT 10
#         """, (groupName,))
#         messages = cur.fetchall()
        
#         last10Messages = [
#             {"mesID": m[0], "mesContent": m[1], "date": m[2], "userName": m[3]} 
#             for m in reversed(messages)
#         ]

#         groups_dict[groupName] = {
#             "last10Messages": last10Messages,
#             "lastReadMessageID": lastReadMessageID
#         }

#     conn.close()

#     return {
#         username: {
#             "userFullName": userFullName,
#             "groups": groups_dict
#         }
#     }


# # Example
# username = "alice"
# data_dict = load_user_data(username)
# print(data_dict)


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


# cur.execute("delete from User")
# conn.commit()

# users = [
#     ("vinh", "Nguyễn Văn Vĩnh", "hash123"),
#     ("duc", "Nguyễn Văn Dục", "hash456"),
#     ("hoa", "Trần Thị Hoa", "hash789"),
# ]

# groups = [
#     ("pythonDev", "1234", "Nhóm học Python", "vinh"),
#     ("gamers", "5678", "Team chơi game", "hoa"),
# ]

# messages = [
#     ("Xin chào mọi người!", "2025-08-27 09:00", "vinh", "pythonDev"),
#     ("Hello Vinh", "2025-08-27 09:05", "hoa", "pythonDev"),
#     ("Hôm nay chơi Liên Minh?", "2025-08-27 10:00", "hoa", "gamers"),
#     ("Ok luôn nè", "2025-08-27 10:10", "duc", "gamers"),
# ]

# members = [
#     ("vinh", "pythonDev", "admin", "2025/08/26 08:00", 2),
#     ("hoa", "pythonDev", "member", "2025/08/26 08:10", 2),
#     ("duc", "gamers", "member", "2025/08/26 09:00", 4),
#     ("hoa", "gamers", "admin", "2025/08/26 09:00", 3),
# ]

# # Insert data
# cur.executemany("INSERT OR IGNORE INTO User VALUES (?, ?, ?)", users)
# cur.executemany("INSERT OR IGNORE INTO GroupChat VALUES (?, ?, ?, ?)", groups)
# cur.executemany("INSERT OR IGNORE INTO Message(mesContent, date, userName, groupName) VALUES (?, ?, ?, ?)", messages)
# cur.executemany("INSERT OR IGNORE INTO MemberOf VALUES (?, ?, ?, ?, ?)", members)

# conn.commit()

conn.close

