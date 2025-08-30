from constant import *
import json
import websockets
from PySide6.QtCore import Signal, QObject
import asyncio
class ClientChat(QObject):
#   --- phan loai signal recv -----
    newMessage = Signal(str)
    searchMessage = Signal(list)
    loginMessage = Signal(str)
    signUpMessage = Signal(str)
    optionMessage = Signal(str)

    def __init__(self):    
        super().__init__()
        self.uri = "ws://26.198.149.7:61000" 

        self.username = None
        self.psw = None 

        self.validcheck = None
        self.msg = "login"

    async def connect(self):
        print("connecting...")
        try:
            self.client = await websockets.connect(self.uri)
            asyncio.create_task(self.listen_server())  # chạy song song lắng nghe
        except:
            print("Cannot connect to server")

#------ dung de loging - signup -------
    def setNamePsw(self, username, psw):
        self.username = username
        self.psw = psw

    async def userLoginSignUp(self, msg):
        self.msg = msg
        fullmsg = {"action": self.msg, "account": self.username, "passw": self.psw}
        jsonStr = json.dumps(fullmsg) + "\n"
        await self.client.send(jsonStr)

    async def searchUser(self,msg,name=None):
        self.msg = msg
        fullmsg = {"action": self.msg, "name": name}
        jsonStr = json.dumps(fullmsg) + "\n"
        await self.client.send(jsonStr)

#-------dung de chat va nhan tin nhan------------------

    async def sendChat(self, type, msg):
        self.msg = msg
        fullmsg = {"action": type, "msg": self.msg}
        jsonStr = json.dumps(fullmsg) + "\n"
        await self.client.send(jsonStr)
    
    async def listen_server(self):
        try:
            async for message in self.client:
                data = json.loads(message)
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
                if action == REQUEST:
                    msg = data.get("mess")  
                    self.optionMessage.emit(msg)
        except:
            print(f"Connection closed: ")

    async def clientSendOption(self,option,user1,user2):
        self.msg = option
        fullmsg = {"action":REQUEST, "option": option, "user1": user1, "user2": user2}
        jsonStr = json.dumps(fullmsg) + "\n"
        await self.client.send(jsonStr)
        



#    def sendList(self, list):
#        self.client.sendall((self.msg + "\n").encode(FORMAT))
#        data = json.dumps(list) + "\n"
#        self.client.sendall(data.encode(FORMAT))