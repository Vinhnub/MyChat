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
    showFriendMessage = Signal(list,list)
    priviteChatMessage = Signal(str, str, str)
    updateStatusMessage = Signal(list)
    updateLastMessage = Signal(str, str,str)
    groupChatMessage = Signal(str,str,str)
    createGroupMessage = Signal(str)
    def __init__(self):    
        super().__init__()
        self.uri = "ws://26.198.149.7:61000" 

        self.username = None
        self.psw = None 

        self.validcheck = None
        self.msg = "login"
        self.listFriendOnline = []
        self.lock = asyncio.Lock()   # lock

    async def safeSend(self, jsonStr):
        async with self.lock:
             await self.client.send(jsonStr)

    async def connect(self):
        print("connecting...")
        try:
            self.client = await websockets.connect(self.uri)
            asyncio.create_task(self.listen_server())  # lắng nghe
        except:
            print("Cannot connect to server")

#------ dung de loging - signup -------
    def setNamePsw(self, username, psw):
        self.username = username
        self.psw = psw

    async def userLoginSignUp(self, action):
        self.msg = action
        fullmsg = {"action": self.msg, "account": self.username, "passw": self.psw}
        jsonStr = json.dumps(fullmsg) + "\n"
        await self.safeSend(jsonStr)

    async def searchUser(self,action,name=None):
        self.msg = action
        fullmsg = {"action": self.msg, "name": name}
        jsonStr = json.dumps(fullmsg) + "\n"
        await self.safeSend(jsonStr)

    async def clientShowFriend(self,action,name):
        self.msg = action
        fullmsg = {"action": self.msg, "name": name}
        jsonStr = json.dumps(fullmsg) + "\n"
        await self.safeSend(jsonStr)

#-------dung de chat va nhan tin nhan------------------

    async def sendChat(self, type, msg):
        self.msg = msg
        fullmsg = {"action": type, "msg": self.msg}
        jsonStr = json.dumps(fullmsg) + "\n"
        await self.safeSend(jsonStr)
    
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
                if action == SHOWFRIEND:
                    frs = data.get("friends")
                    grs = data.get("groups")
                    self.showFriendMessage.emit(frs, grs)
                if action == PRIVATECHAT:
                    msg = data.get("msg")
                    sender = data.get("sender")
                    self.priviteChatMessage.emit(msg,sender,"")
                    self.updateLastMessage.emit(msg,sender,"")

                if action == CHECKSTATUS:
                    msg = data.get("listfriendonl")
                    self.updateStatusMessage.emit(msg)

                if action == GROUPCHAT:
                    msg = data.get("msg")
                    group = data.get("group")
                    self.groupChatMessage.emit(msg,"",group)
                    self.updateLastMessage.emit(msg,"",group)

                if action == CREATEGROUP:
                   msg = data.get("result")
                   self.createGroupMessage.emit(msg)
                
        except:
            print(f"Connection closed: ")

    async def clientSendOption(self,option,user1,user2):
        self.msg = option
        fullmsg = {"action":REQUEST, "option": option, "user1": user1, "user2": user2}
        jsonStr = json.dumps(fullmsg) + "\n"
        await self.safeSend(jsonStr)
        
    async def sendPriviteChat(self,sender,recv,msg):
        self.msg = msg
        fullmsg = {"action": PRIVATECHAT, "sender": sender, "recv": recv, "msg": self.msg}
        jsonStr = json.dumps(fullmsg) + "\n"
        await self.safeSend(jsonStr)

    async def sendGroupChat(self,sender,recv,msg):
        self.msg = msg
        fullmsg = {"action": GROUPCHAT, "sender": sender, "group": recv, "msg": self.msg}
        jsonStr = json.dumps(fullmsg) + "\n"
        await self.safeSend(jsonStr)

    async def getUserOnl(self,listFriend):
        self.msg = CHECKSTATUS
        fullmsg = {"action": CHECKSTATUS, "friends": listFriend}
        jsonStr = json.dumps(fullmsg) + "\n"
        await self.safeSend(jsonStr)
    
    async def createGroup(self, clientName, nameGroup, listAdd):
        self.msg = CREATEGROUP
        fullmsg = {"action": CREATEGROUP,"admin": clientName, "nameGroup": nameGroup, "listAdd": listAdd}
        jsonStr = json.dumps(fullmsg) + "\n"
        await self.safeSend(jsonStr)
     
#    def sendList(self, list):
#        self.client.sendall((self.msg + "\n").encode(FORMAT))
#        data = json.dumps(list) + "\n"
#        self.client.sendall(data.encode(FORMAT))