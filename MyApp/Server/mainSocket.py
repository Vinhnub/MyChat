from constant import *
import sqlite3
import websockets
import json
import asyncio
clients = {} # luu cac client duoi dang conn va name tai khoang
path = r"C:\Users\Lenovo\Desktop\MyChat\mydatabase.db"

print("SERVER SIDE")
print("server:", HOST, SERVER_PORT)
print("Waiting for client")

async def broadcast(msg, sender_name, sender_conn):
    removeWs = []
    fullMsg = {"action": "message", "sender": sender_name, "msg": msg}
    for c in list(clients.keys()):
        if c != sender_conn:
            try:
                await c.send(json.dumps(fullMsg))
            except:
                removeWs.append(c)
    for ws in removeWs:
        await ws.close()
        del clients[ws]

async def serverLogin(ws, msg):
    connDB = sqlite3.connect(path)
    cursor = connDB.cursor()

    #recv account from client
    client_account = msg.get("account")
    client_passw = msg.get("passw")

    cursor.execute("SELECT password FROM useraccount WHERE username = ?", (client_account,))
    results = cursor.fetchone()
    data_password =  results[0]
    if results:
        data_password = results[0]
        if client_passw == data_password:
            result = "login successfully"
            clients[ws] = client_account
        else:
            result = "Invalid password"
    else:
        result = "Username not found"
    fullmsg = {"action": LOGIN, "result": result}
    json_str = json.dumps(fullmsg)
    await ws.send(json_str)

    connDB.close()

async def serverSignUp(ws, msg):
    connDB = sqlite3.connect(path)
    cursor = connDB.cursor()
    #recv account from client
    client_account = msg.get("account")
    client_pass = msg.get("passw")
    cursor.execute("SELECT EXISTS(SELECT 1 FROM useraccount WHERE username=?)", (client_account,))
    exists = cursor.fetchone()[0]
    if exists == 1:
        mess = {"action": "signup", "result": "Username exist!"}

    else:
        cursor.execute("INSERT INTO useraccount (username, password) VALUES (?, ?)", (client_account, client_pass))
        connDB.commit()
        clients[ws] = client_account
        mess = {"action": "signup", "result": " SignUp successfully"}

    print(mess)
    await ws.send(json.dumps(mess))
    connDB.commit()
    connDB.close()
    
async def serverSearch(ws, name):
    users = []
    connDB = sqlite3.connect(path)
    cursor = connDB.cursor()
    if name is None:
        cursor.execute("SELECT * FROM useraccount")
        for row in cursor.fetchall():
            users.append(row[0])
        print(users)
        fullmess = {"action":SEARCH, "mess": users}
    else:
        cursor.execute("SELECT username FROM useraccount where username=?", (name,))
        for row in cursor.fetchall():
            users.append(row[0])
        fullmess = {"action":SEARCH, "mess": users}

    await ws.send(json.dumps(fullmess))

    connDB.close()
        
#--------------- vong lap chinh cua moi thread client ------------
async def handleClient(ws):
    addr = ws.remote_address
    print("client address:", addr)
    clients[ws] = None
    try:
        async for message in ws:
            msg = json.loads(message)  # Chuyển JSON string -> dict
            action = msg.get("action")
            if not msg:
                break
            print(f"client {clients[ws]}, {addr}, acction: {action}")
            if action == LOGIN:
                await serverLogin(ws,msg)
            if action == SIGNUP:
                await serverSignUp(ws,msg)
                
            if action == SEARCH:
                name = msg.get("name")
                await serverSearch(ws,name)
            else:
                if msg.get("msg") == "x":
                    break
                await broadcast(msg.get("msg"),clients[ws], ws)   
    finally:
        print("client", addr, "finished")
        await ws.close()
        if ws in clients:
            del clients[ws]
#----------------main----------------
async def main():
    server = await websockets.serve(handleClient, "127.0.0.1", 5050)
    print("WebSocket server running on ws://127.0.0.1:5050")
    await server.wait_closed()
asyncio.run(main())
