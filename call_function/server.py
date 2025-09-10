from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol

class VoiceServer(DatagramProtocol):
    def __init__(self):
        self.clients = set()

    def datagramReceived(self, data, addr):
        if addr not in self.clients:
            self.clients.add(addr)
            print("[Server] New client:", addr)

        for client in self.clients:
            if client != addr:
                self.transport.write(data, client)

if __name__ == "__main__":
    reactor.listenUDP(5000, VoiceServer(), interface="26.253.176.29")
    print("[Server] UDP Voice Server running on port 5000")
    reactor.run()
