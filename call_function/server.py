import asyncio
import json
from aiohttp import web

rooms = {}  # room_id -> set of websocket connections

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    peer_id = id(ws)
    room = None
    print(f"[Signal] Peer {peer_id} connected")

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            data = json.loads(msg.data)

            # join room
            if data["type"] == "join":
                room = data["room"]
                rooms.setdefault(room, set()).add(ws)
                print(f"[Signal] Peer {peer_id} joined room {room}")

                # thông báo cho các peer khác
                for other in rooms[room]:
                    if other != ws:
                        await other.send_json({
                            "type": "peer-joined",
                            "id": peer_id
                        })

            # relay offer/answer/ice
            elif data["type"] in ["offer", "answer", "ice"]:
                if room and room in rooms:
                    for other in rooms[room]:
                        if other != ws:
                            print(f"[Relay] {data['type']} from {peer_id} -> peer")
                            await other.send_json({
                                "from": peer_id,
                                **data
                            })

        elif msg.type == web.WSMsgType.ERROR:
            print(f"[Error] WS connection closed with exception {ws.exception()}")

    # cleanup
    if room and room in rooms:
        rooms[room].discard(ws)
        if not rooms[room]:
            del rooms[room]
    print(f"[Signal] Peer {peer_id} disconnected")
    return ws

app = web.Application()
app.router.add_get("/ws", websocket_handler)

if __name__ == "__main__":
    web.run_app(app, port=8080)
