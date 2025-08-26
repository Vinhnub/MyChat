from windows import *
import asyncio
import websockets
import json
import threading

class Main():
    def __init__(self, app):
        self.app = app
        self.user = None
        self.loop = None
        self.mainWindow = StartWindow(self.app, self)
        self.secondWindow = None
        self.dataSendQueue = asyncio.Queue()
        threading.Thread(target=lambda: asyncio.run(self.main()), daemon=True).start()

    def show(self):
        self.mainWindow.show()

    def addDataToQueue(self, data):
        asyncio.run_coroutine_threadsafe(self.dataSendQueue.put(data), self.loop)

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
                print(json.loads(msg))
        except websockets.ConnectionClosed:
            print("Lost connection.")

    async def main(self):
        self.loop = asyncio.get_running_loop()
        async with websockets.connect("ws://26.253.176.29:5555") as websocket:
            await asyncio.gather(self.send(websocket), self.recieve(websocket))
    