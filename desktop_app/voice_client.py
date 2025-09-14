import json
import pyaudio
import base64
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
import numpy as np
import json
from constants import *

FORMAT = pyaudio.paInt16

class VoiceClient(DatagramProtocol):
    def __init__(self, main, groupName, username, data):
        self.main = main
        self.groupName = groupName
        self.username = username
        self.memberVolume = {item[0] : 1 for item in data}
        self.micMuted = False
        self.speakerMuted = False
        self.audio = pyaudio.PyAudio()
        self.stream_out = self.audio.open(format=FORMAT, channels=CHANNELS,
                                          rate=RATE, output=True,
                                          frames_per_buffer=CHUNK)
        
        self.stream_in = self.audio.open(format=FORMAT, channels=CHANNELS,
                                         rate=RATE, input=True,
                                         frames_per_buffer=CHUNK)
        

    def startProtocol(self):
        print("[Client] Connected to server via UDP")
        reactor.callInThread(self.record_and_send)

    def record_and_send(self):
        while self.main.isRunningCall:
            data = self.stream_in.read(CHUNK, exception_on_overflow=False)
            packet = {"audio": base64.b64encode(data).decode("utf-8"), "username" : self.username, "groupName" : self.groupName}
            json_packet = json.dumps(packet).encode("utf-8")
            if not self.micMuted and self.transport:
                self.transport.write(base64.b64encode(json_packet), (SERVER_IP, PORT_UDP))

    def datagramReceived(self, datagram, addr):
        if not self.speakerMuted:
            json_packet = base64.b64decode(datagram)
            packet = json.loads(json_packet.decode("utf-8"))
            data = base64.b64decode(packet["audio"])
            print(self.memberVolume)
            if packet["username"] in self.memberVolume:
                audioNp = np.frombuffer(data, dtype=np.int16)
                audioNp = (audioNp * self.memberVolume[packet["username"]]).astype(np.int16)
                self.stream_out.write(audioNp.tobytes())

    def changeVolume(self, username, value):
        if username in self.memberVolume:
            self.memberVolume[username] = value

    def muteMic(self):
        self.micMuted = True

    def unmuteMic(self):
        self.micMuted = False

    def muteSpeaker(self):
        self.speakerMuted = True

    def unmuteSpeaker(self):
        self.speakerMuted = False

# if __name__ == "__main__":
#     voice = VoiceClient("testGroup", "vinh", [("vinh","Nguyễn Văn Vĩnh")])
#     reactor.listenUDP(PORT_UDP, voice, interface=SERVER_IP)  # port 0 = random client port
#     reactor.run(installSignalHandlers=False)