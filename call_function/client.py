import pyaudio
from twisted.internet import reactor, protocol
from twisted.protocols.basic import LineReceiver
import base64

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

class VoiceClient(LineReceiver):
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream_out = self.audio.open(format=FORMAT, channels=CHANNELS,
                                          rate=RATE, output=True,
                                          frames_per_buffer=CHUNK)
        self.stream_in = self.audio.open(format=FORMAT, channels=CHANNELS,
                                         rate=RATE, input=True,
                                         frames_per_buffer=CHUNK)
        reactor.callInThread(self.record_and_send)

    def record_and_send(self):
        while True:
            data = self.stream_in.read(CHUNK, exception_on_overflow=False)
            self.sendLine(base64.b64encode(data))  # gửi base64 để tránh lỗi byte

    def lineReceived(self, line):
        data = base64.b64decode(line)
        self.stream_out.write(data)

class VoiceFactory(protocol.ClientFactory):
    def buildProtocol(self, addr):
        return VoiceClient()

    def clientConnectionFailed(self, connector, reason):
        print("[Client] Connection failed:", reason)
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print("[Client] Connection lost")
        reactor.stop()

if __name__ == "__main__":
    reactor.connectTCP("26.253.176.29", 5000, VoiceFactory())
    reactor.run()
