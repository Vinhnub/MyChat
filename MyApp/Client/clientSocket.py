from constant import *
import json
import socket
from PySide6.QtCore import Signal, QObject
import threading

class ClientChat(QObject):
#   --- phan loai signal recv -----
    newMessage = Signal(str)
    searchMessage = Signal(list)
    loginMessage = Signal(str)
    signUpMessage = Signal(str)

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

    def userLoginSignUp(self, msg):
        self.msg = msg
        fullmsg = {"action": self.msg, "account": self.username, "passw": self.psw}
        json_str = json.dumps(fullmsg) + "\n"
        self.client.sendall(json_str.encode(FORMAT))

    def searchUser(self,msg,name=None):
        self.msg = msg
        fullmsg = {"action": self.msg, "name": name}
        json_str = json.dumps(fullmsg) + "\n"
        self.client.sendall(json_str.encode(FORMAT))

#-------dung de chat va nhan tin nhan------------------ 
    def startListenThread(self):
        threading.Thread(target=self.listen_server, daemon=True).start()

    def sendChat(self, type, msg):
        self.msg = msg
        fullmsg = {"action": type, "msg": self.msg}
        json_str = json.dumps(fullmsg) + "\n"
        self.client.sendall(json_str.encode(FORMAT))
    
    def listen_server(self):
        while True:
            try:
                data = self.client.recv(1024).decode(FORMAT)
                if not data:
                    break
                data = json.loads(data)
                action = data.get("action")

                if action == MESSAGE:
                    msg = f"{data.get('sender')}: {data.get('msg')}"
                    self.newMessage.emit(msg)  # gửi tín hiệu về GUI
                if action == LOGIN:
                    msg = data.get("result")
                    self.loginMessage.emit(msg)
                if action == SIGNUP:
                    msg = data.get("result")
                    self.signUpMessage.emit(msg)
                if action == SEARCH:
                    msg = data.get("mess")
                    self.searchMessage.emit(msg)       
            except:
                break




#    def sendList(self, list):
#        self.client.sendall((self.msg + "\n").encode(FORMAT))
#        data = json.dumps(list) + "\n"
#        self.client.sendall(data.encode(FORMAT))