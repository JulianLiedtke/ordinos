from src.network.local_connector import LocalConnector
from src.network.connection import Channel
from threading import Thread


class Trustee():

    def __init__(self, abb, id):
        self.run_finished = False

        self.id = id
        self.abb = abb

        self.connections = {}

    def setup_connections(self, other_trustees):
        for trustee in other_trustees:
            other_id = trustee.id
            lc = LocalConnector(other_id)
            self.connections[other_id] = lc

    def establish_connections(self, other_trustees):
        for trustee in other_trustees:
            other_id = trustee.id
            self.connections[other_id].connect(trustee.get_connector(self.id))

    def get_connector(self, id):
        return self.connections[id]

    def run_protocol(self, prot, *args):
        self.run_finished = False

        c = Channel(self.id, self.connections.values())
        self.abb.prot_suite.set_connections(c)
        prot.set_connection(c)
        prot.set_abb(self.abb)
        prot.set_output_func(self.receive_prot_output)
        self.protocol = prot

        self.thread = Thread(target=prot.start, args=args)
        self.thread.start()

    def receive_prot_output(self, result):
        self.run_finished = True
        self.result = result

    def is_protocol_finished(self):
        if self.run_finished:
            return True
        if not self.thread.is_alive():
            self.result = "Abort."
            return True
        return False

    def get_protocol(self):
        return self.protocol


def init_trustees(abbs, ids):
    trustees = []
    n_trustees = len(ids)

    # create trustees
    for i in range(n_trustees):
        trustees.append(Trustee(abbs[i], ids[i]))

    # create connectors
    for i in range(n_trustees):
        others = trustees.copy()
        others.pop(i)
        trustees[i].setup_connections(others)

    # establish connections
    for i in range(n_trustees):
        others = trustees.copy()
        others.pop(i)
        trustees[i].establish_connections(others)

    return trustees
