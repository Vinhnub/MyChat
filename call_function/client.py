import json
import pyaudio
import base64
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
import numpy as np
import json

VOLUME = 0.5
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
        
        reactor.callInThread(self.record_and_send)

    def startProtocol(self):
        print("[Client] Connected to server via UDP")

    import json

    def record_and_send(self):
        while True:
            print(1)
            data = self.stream_in.read(CHUNK, exception_on_overflow=False)
            packet = {"audio": base64.b64encode(data).decode("utf-8")}
            json_packet = json.dumps(packet).encode("utf-8")
            self.transport.write(base64.b64encode(json_packet), (SERVER_IP, SERVER_PORT))

    def datagramReceived(self, datagram, addr):
        json_packet = base64.b64decode(datagram)
        packet = json.loads(json_packet.decode("utf-8"))
        data = base64.b64decode(packet["audio"])
        audioNp = np.frombuffer(data, dtype=np.int16)
        audioNp = (audioNp * VOLUME).astype(np.int16)
        self.stream_out.write(audioNp.tobytes())

if __name__ == "__main__":
    reactor.listenUDP(6666, VoiceClient())  # port 0 = random client port
    reactor.run()
