import logging

log = logging.getLogger(__name__)


class Connector():

    def send(self, msg):
        pass

    def receive(self):
        pass


class Channel():

    def __init__(self, id, connectors):
        self.id = id
        self.connectors = connectors

    def broadcast(self, msg):
        for conn in self.connectors:
            conn.send(msg)

    def receive(self):
        msgs = []
        for conn in self.connectors:
            conn_id = conn.id
            msg = conn.receive()
            msgs.append((conn_id, msg))
        return msgs

    def broadcast_and_receive(self, msg):
        self.broadcast(msg)
        response = self.receive()
        response.append((self.id, msg))
        sorted_msgs = sorted(response, key=lambda x: x[0])
        return sorted_msgs
