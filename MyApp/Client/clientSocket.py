import socket
from PySide6.QtCore import Signal, QObject
import threading
HOST = "26.198.149.7" # HOST = "127.0.0.1" #loopback
SERVER_PORT = 61000
FORMAT = "UTF8"
LOGIN = "login"

class ClientChat(QObject):
    newMessage = Signal(str)
    def __init__(self):    
        super().__init__()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.username = None
        self.psw = None 
        self.validcheck = None
        self.connected = False

        self.msg = "login"
        try:
            self.client.connect((HOST, SERVER_PORT))
            self.connected = True
        except:
            print("Cannot connect to server")
#------ dung de loging - signup -------
    def setNamePsw(self, username, psw):
        self.username = username
        self.psw = psw

    def sendList(self, list):
        self.client.sendall((self.msg + "\n").encode(FORMAT))
        self.client.recv(1024)  # chờ server

        for item in list:
            self.client.sendall((item + "\n").encode(FORMAT)) 
            self.client.recv(1024)
        self.client.sendall("end\n".encode(FORMAT))

    def userLoginSignUp(self, msg):
        self.msg = msg
        self.sendList([self.username, self.psw])
        self.validcheck = self.client.recv(1024).decode(FORMAT)
        return self.validcheck

#-------dung de chat va nhan tin nhan------------------ 
    def startListenThread(self):
        threading.Thread(target=self.listen_server, daemon=True).start()

    def sendChat(self, msg):
        self.msg = msg
        self.client.sendall((self.msg + "\n").encode(FORMAT))
    
    def listen_server(self):
        while True:
            try:
                msg = self.client.recv(1024).decode("utf-8")
                if msg:
                    self.newMessage.emit(msg)  # gửi tín hiệu về GUI
            except:
                break

