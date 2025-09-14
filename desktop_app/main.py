from windows import *
import asyncio
import websockets
import json
import threading
from PySide6.QtCore import QObject, Signal
from user import *
from constants import *
from twisted.internet import reactor
from voice_client import *

class Signals(QObject):
    callGui = Signal(object)

class Main():
    def __init__(self, app):
        self.app = app
        self.user = None
        self.voice = None
        self.loop = None
        self.mainWindow = StartWindow(self.app, self)
        self.secondWindow = None
        self.dataSendQueue = asyncio.Queue()
        self.check = None
        self.listeningPort = None
        self.isRunningCall = False

        self.signals = Signals()
        self.signals.callGui.connect(self.handleData)

        threading.Thread(target=lambda: asyncio.run(self.main()), daemon=True).start()
        threading.Thread(target=lambda: reactor.run(installSignalHandlers=False), daemon=True).start()

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

        elif data["type"] == "call":
            self.handleCallResult(data)

        elif data["type"] == "leaveCall":
            self.handleLeaveCallResult(data)

        elif data["type"] == "newMemCall":
            self.handleNewMemCallResult(data)
        
        elif data["type"] == "memLeaveCall":
            self.handleMemLeaveCallResult(data)
            
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

    #============================================= CALL FUNCTION ============================================= 

    def handleCallResult(self, data):
        if data["status"]:
            if self.voice is None:
                self.check = True
                threading.Thread(target=self.startCall, args=(data["groupName"], data["username"], data["data"]), daemon=True).start()
                if self.check:
                    self.secondWindow = CallWindow(self.app, self, data["data"], data["groupName"])
                    self.secondWindow.show()     

    def handleLeaveCallResult(self, data):
        if data["status"]:
            self.stopCall()
            if self.secondWindow is not None:
                self.secondWindow.close()
                self.secondWindow = None
            self.voice = None
            self.check = None

    def handleNewMemCallResult(self, data):
        if self.secondWindow is not None and self.voice is not None:
            username = next(iter(data["info"]))
            self.voice.memberVolume[username] = 1
            self.secondWindow.addMemberIntoCall(data["info"])

    def handleMemLeaveCallResult(self, data):
        if self.secondWindow is not None and self.voice is not None:
            username = data["info"]
            if username in self.voice.memberVolume:
                del self.voice.memberVolume[username]
            self.secondWindow.removeMemberFromCall(username)
     
    def startCall(self, groupName, username, data):
        try:
            self.isRunningCall = True
            self.voice = VoiceClient(self, groupName, username, data)
            def _listen():
                self.listeningPort = reactor.listenUDP(0, self.voice, interface="0.0.0.0")
            reactor.callFromThread(_listen)  # chạy trong reactor thread
        except Exception as e:
            self.check = False

    def stopCall(self):
        self.isRunningCall = False
        if self.listeningPort:
            def _stop():
                try:
                    self.listeningPort.stopListening()
                except Exception as e:
                    pass
            reactor.callFromThread(_stop)
            self.listeningPort = None
            self.voice = None

    def changeVolume(self, username, value):
        if self.voice is not None:
            self.voice.memberVolume[username] = value/100

    def call(self, username, groupName):
        if username and groupName and self.voice is None:
            data = {"type" : "call", "username" : username, "groupName" : groupName}
            self.addDataToQueue(data)

    def muteMic(self):
        self.voice.muteMic()

    def unmuteMic(self):
        self.voice.unmuteMic()

    def muteSpeaker(self):
        self.voice.muteSpeaker()

    def unmuteSpeaker(self):
        self.voice.unmuteSpeaker()     
          
    def leaveCall(self, username, groupName):
        data = {"type" : "leaveCall", "username" : username, "groupName" : groupName}
        self.addDataToQueue(data)

    #==========================================================================================     

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
                self.signals.callGui.emit(data)

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