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
                await c.send(fullMsg)
            except:
                removeWs.append(c)
    for ws in removeWs:
        ws.close()
        del clients[ws]

def serverLogin(ws, msg,cursor):
    #recv account from client
    client_account = msg.get("account")
    client_passw = msg.get("passw")

    cursor.execute("SELECT password FROM useraccount WHERE username = ?", (client_account,))
    results = cursor.fetchone()
    if results:
        data_password = results[0]
        if client_passw == data_password:
            result = "login successfully"
            clients[ws] = client_account
        else:
            result = "Invalid password"
    else:
        result = "Username not found"
    print(result)
    fullmsg = {"action": LOGIN, "result": result}
    jsonStr = json.dumps(fullmsg)
    return jsonStr

def serverSignUp(ws, msg, cursor, connDB):
    #recv account from client
    client_account = msg.get("account")
    client_pass = msg.get("passw")
    cursor.execute("SELECT EXISTS(SELECT 1 FROM useraccount WHERE username=?)", (client_account,))
    exists = cursor.fetchone()[0]
    if exists == 1:
        mess = {"action": "signup", "result": "Username exist!"}

    else:
        cursor.execute("INSERT INTO useraccount (username, password) VALUES (?, ?)", (client_account, client_pass))
        clients[ws] = client_account
        connDB.commit()
        mess = {"action": "signup", "result": " SignUp successfully"}
    jsonStr = json.dumps(mess)
    print(mess)
    return jsonStr

def serverSearch(ws, name,cursor):
    users = []
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
    jsonStr = json.dumps(fullmess)
    return jsonStr
        
#--------------- vong lap chinh cua moi thread client ------------
async def handleClient(ws):
    addr = ws.remote_address
    connDB = sqlite3.connect(path)
    cursor = connDB.cursor()
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
                res = serverLogin(ws,msg,cursor)
                await ws.send(res)
            if action == SIGNUP:
                res = serverSignUp(ws,msg,cursor,connDB)
                await ws.send(res)
            if action == SEARCH:
                name = msg.get("name")
                res = serverSearch(ws,name,cursor)
                await ws.send(res)
            else:
                if msg.get("msg") == "x":
                    break
                await broadcast(msg.get("msg"),clients[ws], ws)  
    finally:
        print("client", addr, "finished")
        await ws.close()
        connDB.close()
        if ws in clients:
            del clients[ws]
#----------------main----------------
async def main():
    server = await websockets.serve(handleClient, "127.0.0.1", 5050)
    print("WebSocket server running on ws://127.0.0.1:5050")
    await server.wait_closed()
asyncio.run(main())
