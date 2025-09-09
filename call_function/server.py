import asyncio
import json
from aiohttp import web, WSMsgType

# rooms: {room_name: {peer_name: websocket}}
rooms = {}

async def ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    room = None
    name = None

    try:
        async for msg in ws:
            if msg.type != WSMsgType.TEXT:
                continue
            data = json.loads(msg.data)

            kind = data.get("type")

            # 1) Client join room
            if kind == "join":
                room = data["room"]
                name = data["name"]

                if room not in rooms:
                    rooms[room] = {}
                rooms[room][name] = ws

                # gửi danh sách peers hiện có cho client mới
                peers = [n for n in rooms[room].keys() if n != name]
                await ws.send_json({"type": "peers", "peers": peers})

                # thông báo cho các peer khác
                await broadcast(room, {"type": "peer-joined", "name": name}, exclude=name)

            # 2) Chuyển tiếp offer/answer/ice theo "to"
            elif kind in ("offer", "answer", "ice"):
                dst = data.get("to")
                if room and dst and room in rooms and dst in rooms[room]:
                    await rooms[room][dst].send_json({
                        "type": kind,
                        "from": name,
                        "data": data.get("data"),
                    })

            # 3) Ping/Pong optional
            elif kind == "ping":
                await ws.send_json({"type": "pong"})

    except asyncio.CancelledError:
        pass
    finally:
        if room and name and room in rooms and name in rooms[room]:
            del rooms[room][name]
            # thông báo rời phòng
            await broadcast(room, {"type": "peer-left", "name": name})
            if not rooms[room]:
                del rooms[room]

    return ws

async def broadcast(room, message, exclude=None):
    if room not in rooms:
        return
    for peer_name, peer_ws in list(rooms[room].items()):
        if exclude and peer_name == exclude:
            continue
        try:
            await peer_ws.send_json(message)
        except Exception:
            pass  # bỏ qua peer lỗi

app = web.Application()
app.router.add_get("/ws", ws_handler)

if __name__ == "__main__":
    web.run_app(app, host="26.253.176.29", port=8765)
