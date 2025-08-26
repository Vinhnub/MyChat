from windows import *
import asyncio
import websockets
import json
import threading
from PySide6.QtCore import QObject, Signal

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

    def show(self):
        self.mainWindow.show()

    def addDataToQueue(self, data):
        asyncio.run_coroutine_threadsafe(self.dataSendQueue.put(data), self.loop)

    def signIn(self):
        pass

    def handleSignUpResult(self, success):
        if self.secondWindow is not None:
            if success:
                self.secondWindow.showSuccess()
            else:
                self.secondWindow.showError()

    def signUp(self, fullname, username, password):
        data = {"type" : "signUp", "fullname" : fullname, "username" : username, "password" : password}
        self.addDataToQueue(data)

    async def send(self, websocket):
        while True:
            try:
                data = await self.dataSendQueue.get()
                await websocket.send(json.dumps(data))
            except:
                pass

    async def recieve(self, websocket):
        try:
            async for msg in websocket:
                data = json.loads(msg)
                print(data)
                if data["type"] == "signUp":
                    self.signals.callGui.emit(lambda: self.handleSignUpResult(data["status"]))

        except websockets.ConnectionClosed:
            print("Lost connection.")

    async def main(self):
        while True:
            try:
                self.loop = asyncio.get_running_loop()
                async with websockets.connect("ws://26.253.176.29:5555") as websocket:
                    await asyncio.gather(self.send(websocket), self.recieve(websocket))
            except:
                await asyncio.sleep(5)  