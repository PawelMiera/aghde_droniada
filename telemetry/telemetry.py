
class Telemetry:
    def __init__(self):
        self.longitude = None
        self.latitude = None
        self.altitude = None
        self.azimuth = None
        self.state = 1

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
        return "{:.7f},{:.7f}".format(self.latitude, self.longitude) + "," + str(self.altitude) + "," +\
               str(self.azimuth) + "," + str(self.state)
        #print("lat", self.latitude, "lon", self.longitude, "alt", self.altitude, "azi", self.azimuth)