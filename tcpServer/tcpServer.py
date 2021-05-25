import asyncore
import socket
import time
import threading


class EchoHandler(asyncore.dispatcher_with_send):

    def __init__(self, sock, telemetry):
        super().__init__(sock)
        self.telemetry = telemetry

    def handle_read(self):
        data = self.recv(8192)
        values = data.decode().split(",")

        for val in values:
            try:
                if val != "":
                    if val[0] == 'l':
                        self.telemetry.latitude = float(val[1:])

                    elif val[0] == 'g':
                        self.telemetry.longitude = float(val[1:])

                    elif val[0] == 'a':
                        self.telemetry.altitude = float(val[1:])

                    elif val[0] == 'y':
                        self.telemetry.azimuth = float(val[1:])

            except Exception:
                pass


class EchoServer(asyncore.dispatcher):

    def __init__(self, host, port, telemetry):
        asyncore.dispatcher.__init__(self)
        self.telemetry = telemetry
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        print('Starting server {} on {}'.format(host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print('Incoming connection from %s' % repr(addr))
            handler = EchoHandler(sock, self.telemetry)
