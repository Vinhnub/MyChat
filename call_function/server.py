from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

clients = []

class VoiceChat(LineReceiver):
    def connectionMade(self):
        clients.append(self)
        print("[Server] Client connected:", self.transport.getPeer())

    def connectionLost(self, reason):
        clients.remove(self)
        print("[Server] Client disconnected")

    def lineReceived(self, line):
        # Broadcast dữ liệu âm thanh tới các client khác
        for c in clients:
            if c != self:
                c.sendLine(line)

factory = Factory()
factory.protocol = VoiceChat

print("[Server] Listening on 0.0.0.0:5000")
reactor.listenTCP(5000, factory)
reactor.run()
