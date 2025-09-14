import json
import pyaudio
import base64
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
import numpy as np
import json

VOLUME = 0.9
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

SERVER_IP = "26.253.176.29"
SERVER_PORT = 5000

class VoiceClient(DatagramProtocol):
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream_out = self.audio.open(format=FORMAT, channels=CHANNELS,
                                          rate=RATE, output=True,
                                          frames_per_buffer=CHUNK)
        
        self.stream_in = self.audio.open(format=FORMAT, channels=CHANNELS,
                                         rate=RATE, input=True,
                                         frames_per_buffer=CHUNK)
        
        self.muted = False
        
        reactor.callInThread(self.record_and_send)

    def startProtocol(self):
        print("[Client] Connected to server via UDP")

    def record_and_send(self):
        while True:
<<<<<<< HEAD
            if self.muted:
                data = b"\x00" * CHUNK * 2
            else:
                data = self.stream_in.read(CHUNK, exception_on_overflow=False)
=======
            print(1)
            data = self.stream_in.read(CHUNK, exception_on_overflow=False)
>>>>>>> 69f48e7fef7745002fed4a083879a5f7b7f9925d
            packet = {"audio": base64.b64encode(data).decode("utf-8")}
            jsonPacket = json.dumps(packet).encode("utf-8")
            self.transport.write(base64.b64encode(jsonPacket), (SERVER_IP, SERVER_PORT))

    def datagramReceived(self, datagram, addr):
        jsonPacket = base64.b64decode(datagram)
        packet = json.loads(jsonPacket.decode("utf-8"))
        data = base64.b64decode(packet["audio"])
        audioNp = np.frombuffer(data, dtype=np.int16)
        audioNp = (audioNp * VOLUME).astype(np.int16)
        self.stream_out.write(audioNp.tobytes())

    def mute(self):
        self.muted = True

    def unmute(self):
        self.muted = False

    def stop(self):
        reactor.callFromThread(reactor.stop)

if __name__ == "__main__":
    vc = VoiceClient()
    reactor.listenUDP(6666, vc)  
    reactor.run()

            
