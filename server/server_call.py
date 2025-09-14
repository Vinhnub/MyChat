from twisted.internet.protocol import DatagramProtocol
import json
import base64

class VoiceServer(DatagramProtocol):
    def __init__(self, listGroups, userOnline):
        self.clients = listGroups
        self.userOnline = userOnline

    def datagramReceived(self, data, addr):
        json_packet = base64.b64decode(data)
        packet = json.loads(json_packet.decode("utf-8"))
        if self.userOnline[packet["username"]]["groupCall"] == packet["groupName"]:
            self.clients[packet["groupName"]]["memberCall"][packet["username"]] = addr

        for client in self.clients[packet["groupName"]]["memberCall"]:
            if client != packet["username"]:
                print(packet["username"], self.clients[packet["groupName"]]["memberCall"], client)
                self.transport.write(data, self.clients[packet["groupName"]]["memberCall"][client])
