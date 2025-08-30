from constant import *
import sqlite3
import websockets
import json
import asyncio
clients = {} # luu cac client duoi dang conn va name tai khoang
path = r"C:\Users\Lenovo\Desktop\MyChat\mydatabaseproject.db"

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

def serverLogin(ws, msg,cursor):
    #recv account from client
    client_account = msg.get("account")
    client_passw = msg.get("passw")

    cursor.execute("SELECT passw FROM account WHERE name = ?", (client_account,))
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
    cursor.execute("SELECT EXISTS(SELECT 1 FROM account WHERE name=?)", (client_account,))
    exists = cursor.fetchone()[0]
    if exists == 1:
        mess = {"action": "signup", "result": "Username exist!"}
    else:
        cursor.execute("INSERT INTO account (name, passw) VALUES (?, ?)", (client_account, client_pass))
        clients[ws] = client_account
        connDB.commit()
        mess = {"action": "signup", "result": " SignUp successfully"}
    jsonStr = json.dumps(mess)
    print(mess)
    return jsonStr

def serverSearch(name,cursor):
    users = []
    if name is None:
        cursor.execute("SELECT * FROM account")
        for row in cursor.fetchall():
            users.append(row[1])
        print(users)
        fullmess = {"action":SEARCH, "mess": users}
    else:
        cursor.execute("SELECT name FROM account where name=?", (name,))
        for row in cursor.fetchall():
            users.append(row[1])
        fullmess = {"action":SEARCH, "mess": users}
    jsonStr = json.dumps(fullmess)
    return jsonStr

def serverRequest(msg, cursor):
    result = ""
    try:
        id1 = cursor.execute("SELECT id from account where name=?", (msg.get("user1"),)).fetchone()[0]
        id2 = cursor.execute("SELECT id from account where name=?", (msg.get("user2"),)).fetchone()[0]
    except:
        print("Error Imformation")
    option = msg.get("option")
    if option == ADD:
       status = cursor.execute("SELECT status FROM status WHERE id1 = ? AND id2 = ?", (id1, id2)).fetchone()[0]
       if status == "friend":
           result = "You are already friends"
       elif status == "block":
           result = "You were blocked"
       else:
           cursor.execute("UPDATE status SET status = ? WHERE id1 = ? AND id2 = ?",("invited", id1, id2))
           result = "Send successfully!"
        
    elif option == UNFRIEND:
        status = cursor.execute("SELECT status FROM status WHERE id1 = ? AND id2 = ?", (id1, id2)).fetchone()[0]
        if status != "friend":
            result = "You are not friends"
        else:
            cursor.execute("UPDATE status SET status = ? WHERE id1 = ? AND id2 = ?",("unfriend", id1, id2))
            result = "Unfriend successfully"
        
    elif option == BLOCK:
        cursor.execute("UPDATE status SET status = ? WHERE id1 = ? AND id2 = ?",("block", id1, id2))
        result = "block!"
    fullmess = {"action": REQUEST, "mess": result}
    jsonStr = json.dumps(fullmess)
    return jsonStr

#--------------- vong lap chinh cua client ------------
async def handleClient(ws):
    addr = ws.remote_address
    connDB = sqlite3.connect(path)
    cursor = connDB.cursor()
    print("client address:", addr)
    clients[ws] = None

    try:
        async for message in ws:
            msg = json.loads(message)
            action = msg.get("action")
            if not msg:
                break
            print(f"client {clients.get(ws)}, {addr}, action: {action}")

            if action == LOGIN:
                res = serverLogin(ws, msg, cursor)
                await ws.send(res)
            elif action == SIGNUP:
                res = serverSignUp(ws, msg, cursor, connDB)
                await ws.send(res)
            elif action == SEARCH:
                name = msg.get("name")
                res = serverSearch(name, cursor)
                await ws.send(res)
            elif action == REQUEST:
                res = serverRequest(msg, cursor)
                connDB.commit()
                await ws.send(res)
            else:
                if msg.get("msg") == "x":
                    break
                await broadcast(msg.get("msg"), clients.get(ws), ws)

    except websockets.exceptions.ConnectionClosedOK:
        print("Client closed connection normally:", addr)
    except websockets.exceptions.ConnectionClosedError:
        print("Client closed connection unexpectedly:", addr)
    finally:
        connDB.close()
        if ws in clients:
            del clients[ws]
        print("client finished:", addr)

#----------------main----------------
async def main():
    server = await websockets.serve(handleClient, HOST, SERVER_PORT)
    print("WebSocket server running")
    await server.wait_closed()
asyncio.run(main())
