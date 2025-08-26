import asyncio
import websockets
import time
import os
import sqlite3
import json

userData = {}
userOnline = {}
groups = {}
conn = sqlite3.connect("Database/chat.db")
cur = conn.cursor()


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
            groups[row[0]] = [row[1]]
        else:
            groups[row[0]].append(row[1])
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