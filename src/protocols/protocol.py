import logging

from src.crypto.abb import Ciphertext
import traceback

log = logging.getLogger(__name__)


class Protocol():

    def __init__(self):
        self.top_protocol = False

        self.abb = None
        self.connection = None

    def init_from_protocol(self, other):
        self.set_connection(other.connection)
        self.set_abb(other.abb)

    def set_output_func(self, output_func):
        self.top_protocol = True
        self.output_func = output_func

    def set_connection(self, connection):
        self.connection = connection

    def set_abb(self, abb):
        self.abb = abb

    def broadcast(self, msg):
        self.connection.broadcast(msg)

    def receive(self):
        return self.connection.receive()

    def broadcast_and_receive(self, msg):
        return self.connection.broadcast_and_receive(msg)

    def start(self, *args):
        try:
            for arg in args:
                if isinstance(arg, Ciphertext):
                    arg.abb = self.abb
            out = self.run(*args)
            if self.top_protocol:
                self.output_func(out)
            return out
        except Exception as e:
            if self.top_protocol:
                log.error('{}'.format(e))
                if log.getEffectiveLevel() == logging.DEBUG:
                    traceback.print_exception(Exception, e, e.__traceback__)
                exit()
            else:
                raise(e)

    def run(self, args):
        return 0

    def run_subprotocol(self, protocol, args):
        protocol.init_from_protocol(self)
        return protocol.start(*args)


class DecProtocol(Protocol):

    def run(self, enc_x):
        return self.abb.dec(enc_x)


class GtDecProtocol(Protocol):

    def run(self, enc_x, enc_y, bits):
        enc_z = self.abb.gt(enc_x, enc_y, bits)
        return self.abb.dec(enc_z)


class EqDecProtocol(Protocol):

    def run(self, enc_x, enc_y, bits):
        enc_z = self.abb.eq(enc_x, enc_y, bits)
        return self.abb.dec(enc_z)


class MulDecProtocol(Protocol):

    def run(self, enc_x, enc_y):
        enc_z = enc_x * enc_y
        return self.abb.dec(enc_z)
