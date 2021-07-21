from socket import socket, gethostname

class ConnectionServer():

    def __init__(self, name, port):
        self.name = name
        self.port = port

    def receive_connections(self):
        s = socket()         # Create a socket object
        host = gethostname()  # Get local machine name
        port = self.port            # Reserve a port for your service.

        s.bind((host, port))        # Bind to the port
        s.listen(5)                 # Now wait for client connection.

        log.info('{} waiting for connections on port {}'.format(self.name, self.port))

        while True:
            conn, addr = s.accept()
            log.info('Connection established by {} ({})'.format(conn, addr))
            
