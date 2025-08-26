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
cur.execute("delete from User")
conn.commit()
conn.close