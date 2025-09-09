import asyncio
import queue
import numpy as np
import sounddevice as sd
from aiortc import MediaStreamTrack
from av import AudioFrame

SAMPLE_RATE = 48000
CHANNELS = 1
CHUNK = 960  # 20ms at 48kHz

class MicStreamTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self, device=None):
        super().__init__()
        self.device = device
        self._q: "queue.Queue[np.ndarray]" = queue.Queue(maxsize=50)
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=CHUNK,
            device=device,
            callback=self._on_audio,
        )
        self._stream.start()

    def _on_audio(self, indata, frames, time, status):  # noqa: N803
        if status:
            # You might want to log status underrun/overrun
            pass
        try:
            self._q.put_nowait(indata.copy())
        except queue.Full:
            # drop if congested
            try:
                _ = self._q.get_nowait()
            except queue.Empty:
                pass
            self._q.put_nowait(indata.copy())

    async def recv(self) -> AudioFrame:
        # Provide a 20ms packet to aiortc
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, self._q.get)
        # data shape: (CHUNK, CHANNELS) int16
        # Convert to (channels, samples)
        pcm = np.transpose(data, (1, 0))
        frame = AudioFrame.from_ndarray(pcm, format="s16", layout="mono" if CHANNELS == 1 else "stereo")
        frame.sample_rate = SAMPLE_RATE
        return frame

class Speaker:
    def __init__(self, device=None):
        self._stream = sd.OutputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=CHUNK,
            device=device,
        )
        self._stream.start()

    def play(self, frame: AudioFrame):
        # frame.pts may be irregular; we simply play ASAP for demo
        pcm = frame.to_ndarray(format="s16")  # (channels, samples)
        # Convert to (samples, channels)
        out = np.transpose(pcm, (1, 0)).copy()
        self._stream.write(out)

    def close(self):
        try:
            self._stream.stop()
            self._stream.close()
        except Exception:
            pass