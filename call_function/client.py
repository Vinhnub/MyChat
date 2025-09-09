import argparse
import asyncio
import json
import aiohttp
import sounddevice as sd
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer, MediaStreamTrack

# ==== Audio Track cho micro ====
class MicrophoneTrack(MediaStreamTrack):
    kind = "audio"
    def __init__(self, device_index=None):
        super().__init__()
        self.device_index = device_index
        self.stream = sd.InputStream(samplerate=48000, channels=1, dtype="int16", device=device_index)
        self.stream.start()

    async def recv(self):
        frame, _ = self.stream.read(960)  # 20ms @ 48kHz
        return self._create_audio_frame(frame, 48000)

# ==== Hàm phát loa ====
class SpeakerPlayer:
    def __init__(self, device_index=None):
        self.device_index = device_index
        self.stream = sd.OutputStream(samplerate=48000, channels=1, dtype="int16", device=device_index)
        self.stream.start()

    async def play_track(self, track):
        while True:
            frame = await track.recv()
            data = frame.to_ndarray()
            self.stream.write(data)

# ==== Client WebRTC ====
async def run(room, stun, mic_index, speaker_index):
    config = RTCConfiguration(iceServers=[RTCIceServer(urls=[stun])] if stun else [])
    pc = RTCPeerConnection(configuration=config)

    # log ICE state
    @pc.on("iceconnectionstatechange")
    def on_ice_state_change():
        print("[ICE] state:", pc.iceConnectionState)

    # log remote track
    speaker = SpeakerPlayer(device_index=speaker_index)
    @pc.on("track")
    def on_track(track):
        print("[Signal] Got remote track:", track.kind)
        if track.kind == "audio":
            asyncio.create_task(speaker.play_track(track))

    # add microphone
    pc.addTrack(MicrophoneTrack(device_index=mic_index))

    # signaling connect
    session = aiohttp.ClientSession()
    ws = await session.ws_connect("http://localhost:8080/ws")

    await ws.send_json({"type": "join", "room": room})
    print(f"[Info] Joined room={room}")

    async def send(msg):
        await ws.send_json(msg)

    # create and send offer
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    await send({"type": "offer", "sdp": offer.sdp, "sdpType": offer.type})

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            data = json.loads(msg.data)

            if data["type"] == "offer":
                print("[Signal] Got offer")
                await pc.setRemoteDescription(RTCSessionDescription(sdp=data["sdp"], type=data["sdpType"]))
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                await send({"type": "answer", "sdp": answer.sdp, "sdpType": answer.type})

            elif data["type"] == "answer":
                print("[Signal] Got answer")
                await pc.setRemoteDescription(RTCSessionDescription(sdp=data["sdp"], type=data["sdpType"]))

            elif data["type"] == "ice":
                print("[Signal] Got ICE")
                candidate = data["candidate"]
                if candidate:
                    await pc.addIceCandidate(candidate)

        elif msg.type == aiohttp.WSMsgType.ERROR:
            print("[Error] ws closed", ws.exception())

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--room", type=str, default="room1")
    parser.add_argument("--stun", type=str, default="stun:stun.l.google.com:19302")
    parser.add_argument("--mic", type=int, default=None, help="Input device index")
    parser.add_argument("--speaker", type=int, default=None, help="Output device index")
    args = parser.parse_args()

    asyncio.run(run(args.room, args.stun, args.mic, args.speaker))
