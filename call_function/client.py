import argparse
import asyncio
import json
import uuid
import numpy as np
import sounddevice as sd
import av
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    RTCIceCandidate,
    RTCConfiguration,
    RTCIceServer,
)

from aiortc.mediastreams import AudioStreamTrack
from websockets import connect

# ================= Microphone Audio Track =================
class MicrophoneStreamTrack(AudioStreamTrack):
    kind = "audio"

    def __init__(self, samplerate=44100, channels=1, blocksize=960, device=None):
        super().__init__()
        self.samplerate = samplerate
        self.channels = channels
        self.blocksize = blocksize  # frames per chunk (20ms @ 48kHz => 960)
        self.device = device
        self._queue = asyncio.Queue()
        self._stream = sd.InputStream(
            channels=self.channels,
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            dtype="float32",
            device=self.device,
            callback=self._callback,
        )
        self._stream.start()

    def _callback(self, indata, frames, time, status):
        if status:
            print("Input status:", status)
        # indata shape: (frames, channels)
        # Convert float32 [-1,1] -> int16
        audio_i16 = np.clip(indata, -1, 1)
        audio_i16 = (audio_i16 * 32767.0).astype(np.int16)
        self._queue.put_nowait(audio_i16)

        # ====== LOG MIC ======
        rms = np.sqrt(np.mean(audio_i16.astype(np.float32) ** 2))
        print(f"[Mic] frames={frames}, rms={rms:.2f}")

    async def recv(self):
        # Lấy một khung từ queue và trả về av.AudioFrame
        pcm = await self._queue.get()
        frame = av.AudioFrame(format="s16", layout="mono" if self.channels == 1 else "stereo",
                              samples=pcm.shape[0])
        # Đổ dữ liệu vào frame
        for plane in frame.planes:
            # plane.buffer là memoryview => ghi dữ liệu
            plane.update(pcm.tobytes())
        frame.sample_rate = self.samplerate
        return frame

    async def stop(self):
        await super().stop()
        if self._stream:
            self._stream.stop()
            self._stream.close()

# ================= Speaker (playback) =================
class SpeakerPlayer:
    """
    Nhận frames từ track và phát ra loa bằng sounddevice.
    Chạy như một task asyncio: speaker.start(track) -> task.
    """
    def __init__(self, samplerate=48000, channels=1, device=None):
        self.samplerate = samplerate
        self.channels = channels
        self.device = device
        self._stream = sd.OutputStream(
            channels=self.channels,
            samplerate=self.samplerate,
            dtype="float32",
            device=self.device,
            blocksize=960,
        )
        self._stream.start()
        self._closed = False

    async def play_track(self, track):
        try:
            while True:
                frame = await track.recv()
                # frame.format = s16, convert -> float32 [-1,1]
                pcm_s16 = frame.to_ndarray()
                if pcm_s16.dtype != np.int16:
                    pcm_s16 = pcm_s16.astype(np.int16)
                pcm_f32 = (pcm_s16.astype(np.float32) / 32767.0)

                # ====== LOG SPEAKER ======
                rms = np.sqrt(np.mean(pcm_f32 ** 2))
                print(f"[Speaker] samples={pcm_f32.shape}, rms={rms:.2f}")

                
                # Nếu stereo/mono mismatch, điều chỉnh
                if pcm_f32.ndim == 1 and self.channels == 2:
                    pcm_f32 = np.stack([pcm_f32, pcm_f32], axis=1)
                elif pcm_f32.ndim == 2 and pcm_f32.shape[1] != self.channels:
                    # ép về mono
                    pcm_f32 = pcm_f32.mean(axis=1, keepdims=True)
                self._stream.write(pcm_f32)
        except asyncio.CancelledError:
            pass
        finally:
            self.close()

    def close(self):
        if not self._closed:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._closed = True

# ================= Signaling helpers =================
async def send(ws, message):
    await ws.send(json.dumps(message))

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="ws://26.253.176.29:8765/ws", help="Signaling WS URL")
    parser.add_argument("--room", default="room1")
    parser.add_argument("--name", default=None, help="Your peer name (default: random)")
    parser.add_argument("--caller", action="store_true", help="Become caller if peers exist")
    parser.add_argument("--mic-index", type=int, default=15, help="sounddevice input device index")
    parser.add_argument("--spk-index", type=int, default=12, help="sounddevice output device index")
    parser.add_argument("--stun", default="stun:stun.l.google.com:19302", help="STUN server URL")
    args = parser.parse_args()

    # In case user wants to list devices
    # print(sd.query_devices())

    name = args.name or f"peer-{uuid.uuid4().hex[:6]}"

    # WebRTC PeerConnection
    # WebRTC PeerConnection (aiortc: dùng RTCConfiguration / RTCIceServer)
    config = RTCConfiguration(
    iceServers=[RTCIceServer(urls=[args.stun])]
    )
    pc = RTCPeerConnection(configuration=config)


    # Mic track
    mic = MicrophoneStreamTrack(device=args.mic_index)
    pc.addTrack(mic)

    # Speaker to play remote audio
    speaker = SpeakerPlayer(device=args.spk_index)
    speaker_task = None  # task chạy playback

    # Signaling websocket
    async with connect(args.server) as ws:
        # Join room
        await send(ws, {"type": "join", "room": args.room, "name": name})

        # ICE candidates local -> gửi qua signaling
        @pc.on("icecandidate")
        async def on_icecandidate(candidate):
            if candidate:
                await send(ws, {
                    "type": "ice",
                    "room": args.room,
                    "name": name,
                    "to": remote_name[0] if remote_name[0] else None,
                    "data": {
                        "candidate": candidate.to_sdp(),
                        "sdpMid": candidate.sdpMid,
                        "sdpMLineIndex": candidate.sdpMLineIndex,
                    }
                })

        remote_name = [None]  # mutable cell

        # Hàm tạo offer tới target
        async def call(target):
            remote_name[0] = target
            offer = await pc.createOffer()
            await pc.setLocalDescription(offer)
            await send(ws, {
                "type": "offer",
                "room": args.room,
                "name": name,
                "to": target,
                "data": {
                    "sdp": pc.localDescription.sdp,
                    "type": pc.localDescription.type
                }
            })

        # Lắng nghe message signaling
        async for message in ws:
            data = json.loads(message)

            typ = data.get("type")

            if typ == "peers":
                peers = data.get("peers", [])
                print(f"[Info] Joined room='{args.room}' as '{name}'. Peers: {peers}")
                # Nếu là caller và có sẵn peer -> gọi peer đầu tiên
                if args.caller and peers:
                    await call(peers[0])

            elif typ == "peer-joined":
                peer = data.get("name")
                print(f"[Signal] Peer joined: {peer}")
                # Nếu là caller và chưa có remote -> gọi ngay
                if args.caller and remote_name[0] is None:
                    await call(peer)

            elif typ == "peer-left":
                peer = data.get("name")
                print(f"[Signal] Peer left: {peer}")

            elif typ == "offer":
                frm = data.get("from")
                sdp = data["data"]["sdp"]
                rtype = data["data"]["type"]
                remote_name[0] = frm

                # Nhận offer -> setRemote -> createAnswer -> send answer
                await pc.setRemoteDescription(RTCSessionDescription(sdp=sdp, type=rtype))
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                await send(ws, {
                    "type": "answer",
                    "room": args.room,
                    "name": name,
                    "to": frm,
                    "data": {
                        "sdp": pc.localDescription.sdp,
                        "type": pc.localDescription.type
                    }
                })

                # Khi đã có remote description, bắt đầu phát loa từ track
                # Tạo task playback cho track audio từ peer
                asyncio.create_task(start_playback(pc, speaker, lambda t: set_speaker_task(t)))

            elif typ == "answer":
                sdp = data["data"]["sdp"]
                rtype = data["data"]["type"]
                await pc.setRemoteDescription(RTCSessionDescription(sdp=sdp, type=rtype))
                # Bắt đầu playback
                asyncio.create_task(start_playback(pc, speaker, lambda t: set_speaker_task(t)))

            elif typ == "ice":
                cand = data["data"]["candidate"]
                sdpMid = data["data"]["sdpMid"]
                sdpMLineIndex = data["data"]["sdpMLineIndex"]
                # cand là dòng candidate trong SDP
                candidate = RTCIceCandidate(
                    sdpMid=sdpMid,
                    sdpMLineIndex=sdpMLineIndex,
                    candidate=cand
                )
                await pc.addIceCandidate(candidate)

        # end for ws

    # Cleanup
    if speaker_task:
        speaker_task.cancel()
    await mic.stop()
    await pc.close()

    def set_speaker_task(task):
        nonlocal speaker_task
        if speaker_task:
            return
        speaker_task = task

async def start_playback(pc: RTCPeerConnection, speaker: SpeakerPlayer, set_task):
    """
    Lấy track audio từ remote và phát.
    Gọi sau khi setRemoteDescription xong (ở offer/answer).
    """
    # Chờ có receiver audio
    # pc.getReceivers() có thể có trước, nhưng track chưa recv ngay -> loop đợi track
    for _ in range(50):
        for r in pc.getReceivers():
            if r.kind == "audio" and r.track:
                task = asyncio.create_task(speaker.play_track(r.track))
                set_task(task)
                return
        await asyncio.sleep(0.1)
    print("[Warn] No remote audio track found to play.")

if __name__ == "__main__":
    asyncio.run(main())
