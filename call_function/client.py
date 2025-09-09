import argparse
import asyncio
import json
import aiohttp
import sounddevice as sd
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer, MediaStreamTrack

# ==== Audio Track cho micro ====
class MicrophoneTrack(MediaStreamTrack):
    kind = "audio"
    def __init__(self, device_index=None):
        super().__init__()
        self.device_index = device_index
        print(f"[Mic] Opening device index={device_index}, samplerate=48000")
        self.stream = sd.InputStream(
            samplerate=48000, channels=1, dtype="int16", device=device_index
        )
        self.stream.start()

    async def recv(self):
        frame, _ = self.stream.read(960)  # ~20ms @ 48kHz
        # log RMS mic
        rms = np.sqrt(np.mean(frame.astype(np.float32) ** 2))
        print(f"[Mic] Captured {frame.shape} samples, rms={rms:.2f}")
        return self._create_audio_frame(frame, 48000)

    def stop(self):  # sync (không còn warning)
        print("[Mic] Stopping microphone stream...")
        try:
            self.stream.stop()
            self.stream.close()
        except Exception as e:
            print("[Mic] stop error:", e)
        super().stop()

# ==== Hàm phát loa ====
class SpeakerPlayer:
    def __init__(self, device_index=None):
        self.device_index = device_index
        print(f"[Speaker] Opening device index={device_index}, samplerate=48000")
        self.stream = sd.OutputStream(
            samplerate=48000, channels=1, dtype="int16", device=device_index
        )
        self.stream.start()

    async def play_track(self, track):
        while True:
            frame = await track.recv()
            data = frame.to_ndarray()
            # log RMS speaker
            rms = np.sqrt(np.mean(data.astype(np.float32) ** 2))
            print(f"[Speaker] Playing {data.shape} samples, rms={rms:.2f}")
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
    ws = await session.ws_connect("http://26.253.176.29:8080/ws")

    await ws.send_json({"type": "join", "room": room})
    print(f"[Signal] connected to http://26.253.176.29:8080/ws. joining room={room}")

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
                print("[Signal] Got OFFER")
                await pc.setRemoteDescription(RTCSessionDescription(sdp=data["sdp"], type=data["sdpType"]))
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                await send({"type": "answer", "sdp": answer.sdp, "sdpType": answer.type})

            elif data["type"] == "answer":
                print("[Signal] Got ANSWER")
                await pc.setRemoteDescription(RTCSessionDescription(sdp=data["sdp"], type=data["sdpType"]))

            elif data["type"] == "ice":
                print("[Signal] Got ICE candidate")
                candidate = data["candidate"]
                if candidate:
                    await pc.addIceCandidate(candidate)

        elif msg.type == aiohttp.WSMsgType.ERROR:
            print("[Error] ws closed", ws.exception())

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--room", type=str, default="room1")
    parser.add_argument("--stun", type=str, default="stun:stun.l.google.com:19302")
    parser.add_argument("--mic", type=int, default=9, help="Input device index")
    parser.add_argument("--speaker", type=int, default=8, help="Output device index")
    args = parser.parse_args()

    asyncio.run(run(args.room, args.stun, args.mic, args.speaker))