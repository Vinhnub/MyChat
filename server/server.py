import asyncio
import websockets
import time
import os
import sqlite3
import json

userData = {}
userOnline = {}
groups = {}
conn = sqlite3.connect("database/chat.db")
cur = conn.cursor()

def loadDataFor(username):
    global userOnline, conn, cur

    cur.execute("SELECT userFullName FROM User WHERE userName=?", (username,))
    userRow = cur.fetchone()
    if not userRow:
        return  

    userFullName = userRow[0]

    cur.execute("""
        SELECT groupName, lastReadMessageID 
        FROM MemberOf 
        WHERE userName=?
    """, (username,))
    groupsRows = cur.fetchall()

    groupsDict = {}

    for groupName, lastReadMessageID in groupsRows:
        cur.execute("""
            SELECT mesID, mesContent, date, userName 
            FROM Message
            WHERE groupID = (SELECT rowid FROM GroupChat WHERE groupName=?)
            ORDER BY mesID DESC
        """, (groupName,))
        messages = cur.fetchall()
        
        lastMessages = [
            {"mesID": m[0], "mesContent": m[1], "date": m[2], "userName": m[3]} 
            for m in reversed(messages)
        ]

        groupsDict[groupName] = {
            "lastMessages": lastMessages,
            "lastReadMessageID": lastReadMessageID
        }

    if username not in userOnline:
        userOnline[username] = {"userFullName" : userFullName, "groups" : groupsDict}
    
    return {"userFullName": userFullName, "groups": groupsDict}
    

def loadUserData():
    global userData, conn, cur
    cur.execute("SELECT userName, userPasswordHash FROM User;")
    userData = {row[0] : row[1] for row in cur.fetchall()}
    print(userData)

def loadGroup():
    global groups, conn, cur
    cur.execute("SELECT groupName, userName FROM MemberOf;")
    for row in cur.fetchall():
        if row[0] not in groups:
            groups[row[0]] = {"members" : [row[1]]}
        else:
            groups[row[0]]["members"].append(row[1])
    cur.execute("select groupName, groupPassword from GroupChat")
    for row in cur.fetchall():
        groups[row[0]]["password"] = row[1]
    print(groups)

def register(fullname, username, password):
    global userData, conn, cur
    userData[username] = password
    cur.execute("Insert into User (userName, userFullName, userPasswordHash) values (?, ?, ?)", (username, fullname, password))
    conn.commit()

async def handleClient(websocket):
    print("New client connected.")
    username = None
    try:
        async for msg in websocket:
            data = json.loads(msg)
            print(data)
            if data["type"] == "signUp":
                if data["username"] in userData:
                    responseData = {"type" : "signUp", "status" : False}
                    await websocket.send(json.dumps(responseData))
                else:
                    register(data["fullname"], data["username"], data["password"])
                    responseData = {"type" : "signUp", "status" : True}
                    await websocket.send(json.dumps(responseData))

            if data["type"] == "singIn":
                if data["username"] in userOnline:
                    responseData = {"type" : "signIn", "status" : "error", "data" : None} # error happen when user already online and someone try to login
                    await websocket.send(json.dumps(responseData))
                elif userData[data["username"]] != data["password"]:
                    responseData = {"type" : "signIn", "status" : False, "data" : None} 
                    await websocket.send(json.dumps(responseData))
                else:
                    dataOfUser = loadDataFor(data["username"])
                    responseData = {"type" : "signIn", "status" : True, "data" : dataOfUser}
                    await websocket.send(json.dumps(responseData)) 
                    

    except websockets.exceptions.ConnectionClosed:
        print(f"{username} disconnected.")    
    
    finally:
        if username in userOnline:
            del userOnline[username]

# start the websocket server
async def start_server():
    try:
        loadUserData()
        loadGroup()
        async with websockets.serve(handleClient, "26.253.176.29", 5555):
            print('Websockets Server Started')
            await asyncio.Future()
    finally:
        conn.close()

asyncio.run(start_server())