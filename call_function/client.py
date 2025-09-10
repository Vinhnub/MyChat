import pyaudio
import base64
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol

CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

SERVER_IP = "26.253.176.29"
SERVER_PORT = 5000

class VoiceClient(DatagramProtocol):
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        # Mở loa
        self.stream_out = self.audio.open(format=FORMAT, channels=CHANNELS,
                                          rate=RATE, output=True,
                                          frames_per_buffer=CHUNK)
        # Mở micro
        self.stream_in = self.audio.open(format=FORMAT, channels=CHANNELS,
                                         rate=RATE, input=True,
                                         frames_per_buffer=CHUNK)
        reactor.callInThread(self.record_and_send)

    def startProtocol(self):
        print("[Client] Connected to server via UDP")

    def record_and_send(self):
        while True:
            data = self.stream_in.read(CHUNK, exception_on_overflow=False)
            self.transport.write(base64.b64encode(data), (SERVER_IP, SERVER_PORT))

    def datagramReceived(self, datagram, addr):
        data = base64.b64decode(datagram)
        self.stream_out.write(data)

if __name__ == "__main__":
    reactor.listenUDP(0, VoiceClient())  # port 0 = random client port
    reactor.run()