import asyncio
import websockets
import time
import os
import sqlite3
import json

userData = {}
userOnline = {}
groups = {}



async def loadUserData():
    global userData
    conn = sqlite3.connect("Database/chat.db")
    cur = conn.cursor()
    cur.execute("SELECT userName, userPasswordHash FROM User;")
    userData = {row[0] : row[1] for row in cur.fetchall()}
    conn.close()
    print(userData)

async def signIn(websocket, data):
    pass

async def signUp(data):
    pass

async def loadGroup():
    global groups
    conn = sqlite3.connect("Database/chat.db")
    cur = conn.cursor()
    cur.execute("SELECT groupName, userName FROM MemberOf;")
    for row in cur.fetchall():
        if row[0] not in groups:
            groups[row[0]] = [row[1]]
        else:
            groups[row[0]].append(row[1])
    conn.close()
    print(groups)

async def handleClient(websocket):
    print("New client connected.")
    username = None
    try:
        async for msg in websocket:
            data = json.loads(msg)

    except websockets.exceptions.ConnectionClosed:
        print(f"{username} disconnected.")    
    
    finally:
        if username in userOnline:
            del userOnline[username]

# start the websocket server
async def start_server():
    await loadUserData()
    await loadGroup()
    async with websockets.serve(handleClient, "26.253.176.29", 5555):
        print('Websockets Server Started')
        await asyncio.Future()


asyncio.run(start_server())