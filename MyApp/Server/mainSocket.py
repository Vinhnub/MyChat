from constant import *
import sqlite3
import socket
import threading
import json

clients = {} # luu cac client duoi dang conn va name tai khoang
path = r"C:\Users\Lenovo\Desktop\MyChat\mydatabase.db"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, SERVER_PORT))
s.listen()

print("SERVER SIDE")
print("server:", HOST, SERVER_PORT)
print("Waiting for client")

def broadcast(msg, sender_name, sender_conn):
    fullMsg = {"action": "message", "sender": sender_name, "msg": msg}
    for c in list(clients.keys()):
        if c != sender_conn:
            try:
                c.sendall(json.dumps(fullMsg).encode(FORMAT))
            except:
                c.close()
                del clients[c]

def serverLogin(conn, msg):
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
            clients[conn] = client_account
        else:
            result = "Invalid password"
    else:
        msg = "Username not found"
    fullmsg = {"action": LOGIN, "result": result}
    json_str = json.dumps(fullmsg)
    conn.sendall(json_str.encode(FORMAT))

    connDB.close()

def serverSignUp(conn, msg):
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
        clients[conn] = client_account
        mess = {"action": "signup", "result": " SignUp successfully"}

    print(mess)
    conn.sendall(json.dumps(mess).encode(FORMAT))
    connDB.commit()
    connDB.close()
    
def serverSearch(conn, name):
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

    conn.sendall(json.dumps(fullmess).encode(FORMAT))

    connDB.commit()
    connDB.close()
        
#--------------- vong lap chinh cua moi thread client ------------
def handleClient(conn: socket, addr):
    print("client address:", addr)
    print("conn:", conn.getsockname())
    msg = None
    while msg != "x":
        data = conn.recv(1024).decode(FORMAT).strip()
        msg = json.loads(data)  # Chuyển JSON string -> dict
        action = msg.get("action") # strip bỏ \n
        if not msg:
            break
        print(f"client {clients[conn]}, {addr}, acction: {action}")
        if action == LOGIN:
            serverLogin(conn,msg)
        if action == SIGNUP:
            serverSignUp(conn,msg)
        if action == SEARCH:
            name = msg.get("name")
            serverSearch(conn,name)
        else:
            if msg.get("msg") == "x":
                break
            broadcast(msg.get("msg"),clients[conn], conn)

    print("client", addr, "finished")
    print(conn.getsockname(), "close")
    conn.close()
    if conn in clients:
        del clients[conn]
#------------ vong lap chinh tao ra thread cho moi client moi ket noi-----------
nClient = 0
while (nClient < 5):
    try: 
        conn, addr = s.accept()
        clients[conn] = None  # luu client duoi dang conn va name tai khoang
        thr = threading.Thread(target=handleClient, args=(conn, addr))
        thr.daemon = False
        thr.start()
    except:
        print("Error")
    nClient += 1
print("END")
input()
s.close()




#    try:
#        data = conn.recv(1024).decode(FORMAT).strip()  # nhận 1 lần
#        items = json.loads(data)  # parse JSON thành list
#        return items
#    except Exception as e:
#        print("Error in recvList:", e)
#        return []