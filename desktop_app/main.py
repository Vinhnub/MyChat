from windows import *
import asyncio
import websockets
import json
import threading
from PySide6.QtCore import QObject, Signal
from user import *
from constants import *

class Signals(QObject):
    callGui = Signal(object)

class Main():
    def __init__(self, app):
        self.app = app
        self.user = None
        self.loop = None
        self.mainWindow = StartWindow(self.app, self)
        self.secondWindow = None
        self.dataSendQueue = asyncio.Queue()

        self.signals = Signals()
        self.signals.callGui.connect(self.handleCallGui)

        threading.Thread(target=lambda: asyncio.run(self.main()), daemon=True).start()

    def handleCallGui(self, func):
        func()
        
    def handleData(self, data):
        if data["type"] == "signUp":
            self.handleSignUpResult(data["status"])
        
        elif data["type"] == "signIn":
            self.handleSignInResult(data)
        
        elif data["type"] == "recvMessage":
            self.handleRecvMessage(data)
        
        elif data["type"] == "logout":
            self.handleLogoutResult(data)

        elif data["type"] == "createGroup":
            self.handleCreateGroupResult(data)

        elif data["type"] == "joinGroup":
            self.handleJoinGroupResult(data)
            
    def handleSignUpResult(self, success):
        if self.secondWindow is not None:
            if success:
                self.secondWindow.showSuccess()
            else:
                self.secondWindow.showError()
            
    def handleSignInResult(self, data):
        if data["status"] == False or data["status"] == "error":
            self.secondWindow.showError()
        else:
            self.secondWindow.close()
            dataFilter = {}
            for groupName in data["data"]["groups"].keys():
                dataFilter[groupName] = data["data"]["groups"][groupName]["listMsg"]
            print(dataFilter)
            self.user = User(data["data"]["username"], data["data"]["userFullName"], dataFilter)
            self.mainWindow = ChatWindow(self.app, self, data, dataFilter)
            self.mainWindow.show()

    def handleRecvMessage(self, data):
        self.mainWindow.recvMessage(data["message"])

    def handleLogoutResult(self, data):
        if data["status"]:
            self.mainWindow.close()
            self.mainWindow = StartWindow(self.app, self)
            self.mainWindow.show()
            self.user = None

    def handleCreateGroupResult(self, data):
        if data["status"]:
            self.secondWindow.showSuccess()
            self.mainWindow.addGroup(data["data"])
        else:
            self.secondWindow.showError()

    def handleJoinGroupResult(self, data):
        if data["status"]:
            self.secondWindow.close()
            self.mainWindow.addGroup(data["data"])
        else:
            self.secondWindow.showError() 

    def signIn(self, username, password):
        data = {"type" : "signIn", "username" : username, "password" : password}
        self.addDataToQueue(data)

    def signUp(self, fullname, username, password):
        data = {"type" : "signUp", "fullname" : fullname, "username" : username, "password" : password}
        self.addDataToQueue(data)

    def sendMessage(self, msg):
        data = {"type" : "sendMessage", "message" : msg}
        self.addDataToQueue(data)

    def logout(self, username):
        data = {"type" : "logout", "username" : username}
        self.addDataToQueue(data)

    def createGroup(self, groupDes, groupName, groupPassword, myname):
        data = {"type" : "createGroup", "groupDes" : groupDes, "groupName" : groupName, "groupPassword" : groupPassword, "username" : myname}
        self.addDataToQueue(data)

    def joinGroup(self, groupName, groupPassword, myName):
        data = {"type" : "joinGroup", "groupName" : groupName, "groupPassword" : groupPassword, "username" : myName}
        self.addDataToQueue(data)

    def addDataToQueue(self, data):
        asyncio.run_coroutine_threadsafe(self.dataSendQueue.put(data), self.loop)

    def show(self):
        self.mainWindow.show()

    async def send(self, websocket):
        while True:
            try:
                data = await self.dataSendQueue.get()
                print(data)
                await websocket.send(json.dumps(data))
            except:
                pass

    async def recieve(self, websocket):
        try:
            async for msg in websocket:
                data = json.loads(msg)
                print(data)
                self.signals.callGui.emit(lambda: self.handleData(data))

        except websockets.ConnectionClosed:
            print("Lost connection.")

    async def main(self):
        while True:
            try:
                self.loop = asyncio.get_running_loop()
                async with websockets.connect(f"ws://{SERVER_IP}:{PORT_TCP}") as websocket:
                    await asyncio.gather(self.send(websocket), self.recieve(websocket))
            except:
                await asyncio.sleep(1)  