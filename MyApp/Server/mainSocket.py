import sqlite3
import socket
import threading
import pyodbc
HOST = "26.198.149.7" #loopback
SERVER_PORT = 61000
FORMAT = "UTF8"
LOGIN = "login"
SIGNUP = "signup"
clients = {} # luu cac client duoi dang conn va name tai khoang
db_path = r"C:\Users\Lenovo\Desktop\MyChat\mydatabase.db"

def broadcast(msg, sender_name):
    fullMsg = f"{sender_name}: {msg}"
    for c in list(clients.keys()):
        try:
            c.sendall(fullMsg.encode(FORMAT))
        except:
            c.close()
            del clients[c]

def recvList(conn):
    list = []
    item = conn.recv(1024).decode(FORMAT).strip()
    while item != "end":
        list.append(item)
        conn.sendall("ack\n".encode(FORMAT))  # gửi ack
        item = conn.recv(1024).decode(FORMAT).strip()
    return list

def serverLogin(conn):
    connDB = sqlite3.connect(db_path)
    cursor = connDB.cursor()
    #recv account from client
    client_account = recvList(conn)
    cursor.execute("SELECT password FROM useraccount WHERE username = ?", (client_account[0],))
    result = cursor.fetchone()
    data_password =  result[0]

    msg = "SeverReply"
    if (client_account[1] == data_password):
        msg = "login successfully"
        clients[conn] = client_account[0] # luu client duoi dang conn va name tai khoang
        print(msg)
        print(clients[conn])
    else:
        msg = "Invalid password"
        print(msg)  
    connDB.close()
    conn.sendall(msg.encode(FORMAT))

def serverSignUp(conn):
    connDB = sqlite3.connect(db_path)
    cursor = connDB.cursor()
    #recv account from client
    client_account = recvList(conn)
    cursor.execute("SELECT EXISTS(SELECT 1 FROM useraccount WHERE username=?)", (client_account[0],))
    exists = cursor.fetchone()[0]
    if exists == 1:
        msg = "Username exist!"
        print(msg)
        conn.sendall(msg.encode(FORMAT))
    else:
        cursor.execute("INSERT INTO useraccount (username, password) VALUES (?, ?)", (client_account[0], client_account[1]))
        connDB.commit()
        clients[conn] = client_account[0]
        msg = "login successfully"
    print(msg)
    conn.sendall(msg.encode(FORMAT))
    connDB.close()
#--------------- vong lap chinh cua moi thread client ------------
def handleClient(conn: socket, addr):
    print("client address:", addr)
    print("conn:", conn.getsockname())
    msg = None
    while msg != "x":
        msg = conn.recv(1024).decode(FORMAT).strip()  # strip bỏ \n
        if not msg:
            break
        print(f"client {clients[conn]}, {addr}, say: {msg}")
        if msg == LOGIN:
            conn.sendall("ack\n".encode(FORMAT))  # gửi ack cho client
            serverLogin(conn)
        if msg == SIGNUP:
            conn.sendall("ack\n".encode(FORMAT))  # gửi ack cho client
            serverSignUp(conn)
        else:
            broadcast(msg, clients[conn])

    print("client", addr, "finished")
    print(conn.getsockname(), "close")
    conn.close()
    if conn in clients:
        del clients[conn]

#------------------------------------------

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, SERVER_PORT))
s.listen()

print("SERVER SIDE")
print("server:", HOST, SERVER_PORT)
print("Waiting for client")

#------------ vong lap chinh tao ra thread cho moi client moi ket noi-----------
nClient = 0
while (nClient < 3):
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
conx.close()