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

    def __init__(self, samplerate=48000, channels=1, blocksize=960, device=None):
        super().__init__()  # 初始化 MediaStreamTrack
        self.device = device

        # Query device info and pick valid channels / samplerate
        try:
            info = sd.query_devices(device, 'input')
            maxch = int(info.get('max_input_channels', 1))
            default_sr = int(info.get('default_samplerate', samplerate))
        except Exception as e:
            print("[Mic] query_devices error:", e)
            maxch = channels
            default_sr = samplerate

        self.channels = min(channels, max(1, maxch))
        self.samplerate = default_sr
        self.blocksize = blocksize
        self._queue = asyncio.Queue()

        print(f"[Mic] Opening device index={device}, name='{info.get('name','?')}', "
              f"channels={self.channels}, samplerate={self.samplerate}")

        # Use try/except to surface opening errors
        try:
            self._stream = sd.InputStream(
                device=self.device,
                channels=self.channels,
                samplerate=self.samplerate,
                blocksize=self.blocksize,
                dtype="float32",
                callback=self._callback,
                # extra_settings optional...
            )
            self._stream.start()
        except Exception as e:
            print("[Mic] Error opening InputStream:", e)
            raise

    def _callback(self, indata, frames, time, status):
        if status:
            print("[Mic] Input status:", status)
        # indata shape: (frames, channels)
        # Convert float32 [-1,1] -> int16
        audio_i16 = np.clip(indata, -1, 1)
        audio_i16 = (audio_i16 * 32767.0).astype(np.int16)
        # put into queue (shape: frames x channels)
        try:
            self._queue.put_nowait(audio_i16)
        except Exception as e:
            print("[Mic] Queue put error:", e)

        # ====== LOG MIC ======
        rms = np.sqrt(np.mean(audio_i16.astype(np.float32) ** 2))
        print(f"[Mic] frames={frames}, shape={audio_i16.shape}, rms={rms:.2f}")

    async def recv(self):
        pcm = await self._queue.get()
        # pcm shape: (frames, channels)
        frames = pcm.shape[0]
        layout = "mono" if self.channels == 1 else "stereo"
        frame = av.AudioFrame(format="s16", layout=layout, samples=frames)
        for plane in frame.planes:
            plane.update(pcm.tobytes())
        frame.sample_rate = self.samplerate
        return frame

    async def stop(self):
        await super().stop()
        if hasattr(self, "_stream") and self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass

# ================= Speaker (playback) =================
class SpeakerPlayer:
    """
    Nhận frames từ track và phát ra loa bằng sounddevice.
    Chạy như một task asyncio: speaker.play_track(track) -> task.
    """
    def __init__(self, samplerate=48000, channels=1, device=None):
        self.samplerate = samplerate
        self.channels = channels
        self.device = device
        self._closed = False

        # Query output device to choose valid channel count
        try:
            info = sd.query_devices(device, 'output')
            maxout = int(info.get('max_output_channels', 2))
        except Exception as e:
            print("[Speaker] query_devices error:", e)
            maxout = channels

        self.channels = min(self.channels, max(1, maxout))
        print(f"[Speaker] Opening device index={device}, channels={self.channels}, samplerate={self.samplerate}")

        try:
            self._stream = sd.OutputStream(
                device=self.device,
                channels=self.channels,
                samplerate=self.samplerate,
                dtype="float32",
                blocksize=960,
            )
            self._stream.start()
        except Exception as e:
            print("[Speaker] Error opening OutputStream:", e)
            raise

    async def play_track(self, track):
        print("[Speaker] play_track started for track:", track)
        try:
            while True:
                # Wait for remote frame
                frame = await track.recv()
                if frame is None:
                    print("[Speaker] Received None frame")
                    continue

                # Convert to ndarray
                pcm = frame.to_ndarray()
                # Normalize/convert s16 -> float32 in range [-1,1] if needed
                if pcm.dtype == np.int16:
                    pcm_f32 = pcm.astype(np.float32) / 32767.0
                elif pcm.dtype == np.float32:
                    pcm_f32 = pcm
                else:
                    pcm_f32 = pcm.astype(np.float32) / np.iinfo(pcm.dtype).max

                # LOG
                rms = np.sqrt(np.mean(pcm_f32 ** 2))
                print(f"[Speaker] samples={pcm_f32.shape}, dtype={pcm.dtype}, rms={rms:.4f}")

                # Shape adjustments
                if pcm_f32.ndim == 1 and self.channels == 2:
                    pcm_f32 = np.stack([pcm_f32, pcm_f32], axis=1)
                elif pcm_f32.ndim == 2 and pcm_f32.shape[1] != self.channels:
                    # mix-down or upmix
                    if self.channels == 1:
                        pcm_f32 = pcm_f32.mean(axis=1, keepdims=True)
                    else:
                        # repeat first channel
                        pcm_f32 = np.tile(pcm_f32[:, :1], (1, self.channels))

                # sounddevice expects shape (frames, channels) for float32
                try:
                    self._stream.write(pcm_f32)
                except Exception as e:
                    print("[Speaker] OutputStream write error:", e)
        except asyncio.CancelledError:
            print("[Speaker] play_track cancelled")
        except Exception as e:
            print("[Speaker] play_track error:", e)
        finally:
            self.close()

    def close(self):
        if not self._closed:
            try:
                if hasattr(self, "_stream") and self._stream:
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

    name = args.name or f"peer-{uuid.uuid4().hex[:6]}"

    # WebRTC PeerConnection (aiortc: dùng RTCConfiguration / RTCIceServer)
    config = RTCConfiguration(iceServers=[RTCIceServer(urls=[args.stun])])
    pc = RTCPeerConnection(configuration=config)

    # place-holder for speaker task
    speaker_task = None

    # Speaker to play remote audio (create BEFORE on("track") handler so closure sees it)
    speaker = SpeakerPlayer(samplerate=48000, channels=1, device=args.spk_index)

    def set_speaker_task(task):
        nonlocal speaker_task
        if speaker_task:
            return
        speaker_task = task

    # on track event (use this instead of polling)
    @pc.on("track")
    def on_track(track):
        print("[Signal] Got remote track:", track.kind)
        if track.kind == "audio":
            # start playback task
            task = asyncio.create_task(speaker.play_track(track))
            set_speaker_task(task)

    # ICE state logging
    @pc.on("iceconnectionstatechange")
    def on_ice_state_change():
        print("[ICE] state:", pc.iceConnectionState)

    # Mic track
    mic = MicrophoneStreamTrack(samplerate=48000, channels=1, device=args.mic_index)
    pc.addTrack(mic)

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
                if args.caller and peers:
                    await call(peers[0])

            elif typ == "peer-joined":
                peer = data.get("name")
                print(f"[Signal] Peer joined: {peer}")
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

                print("[Signal] Received offer from", frm)
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

            elif typ == "answer":
                print("[Signal] Received answer")
                sdp = data["data"]["sdp"]
                rtype = data["data"]["type"]
                await pc.setRemoteDescription(RTCSessionDescription(sdp=sdp, type=rtype))

            elif typ == "ice":
                cand = data["data"]["candidate"]
                sdpMid = data["data"]["sdpMid"]
                sdpMLineIndex = data["data"]["sdpMLineIndex"]
                candidate = RTCIceCandidate(
                    sdpMid=sdpMid,
                    sdpMLineIndex=sdpMLineIndex,
                    candidate=cand
                )
                try:
                    await pc.addIceCandidate(candidate)
                except Exception as e:
                    print("[ICE] addIceCandidate error:", e)

    # end websocket

    # Cleanup
    if speaker_task:
        speaker_task.cancel()
    await mic.stop()
    await pc.close()

if __name__ == "__main__":
    asyncio.run(main())
