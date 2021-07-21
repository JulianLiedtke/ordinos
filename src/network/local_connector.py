import logging
from time import sleep

from src.network.connection import Connector

log = logging.getLogger(__name__)


class LocalConnector(Connector):

    def __init__(self, id):
        self.id = id
        self.stream = []

    def connect(self, connection):
        self.connection = connection

    def send(self, msg):
        self.connection.receive_next_msg(msg)

    def receive_next_msg(self, msg):
        self.stream.append(msg)

    def receive(self):
        while len(self.stream) == 0:
            sleep(0.01)
        return self.stream.pop(0)
