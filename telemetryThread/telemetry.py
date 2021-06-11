import threading
from tcpServer.tcpServer import *


class TelemetryThread:
    def __init__(self):
        self.longitude = 0
        self.latitude = 0
        self.altitude = 0
        self.azimuth = 0
        self.state = 1

        self.server = EchoServer('127.0.0.1', 6969, self)
        self.thread = threading.Thread(target=self.start_thread)
        self.thread.daemon = True
        self.thread.start()

    def start_thread(self):
        asyncore.loop()

    def update_telemetry(self, data):
        self.latitude = float(data[0])
        self.longitude = float(data[1])
        self.altitude = float(data[2])
        self.azimuth = float(data[3])

        """self.latitude = 52.085234
        self.longitude = 18.869299
        self.altitude = 15
        self.azimuth = 280"""

    def update_telemetry_manually(self, longitude, latitude, altitude, azimuth, state):
        self.longitude = longitude
        self.latitude = latitude
        self.altitude = altitude
        self.azimuth = azimuth
        self.state = state

    def to_string(self):
        return "{:.7f},{:.7f}".format(self.latitude, self.longitude) + "," + str(self.altitude) + "," + \
               str(self.azimuth) + "," + str(self.state)
        #print("lat", self.latitude, "lon", self.longitude, "alt", self.altitude, "azi", self.azimuth)

    def close(self):
        asyncore.close_all()