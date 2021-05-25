
class Telemetry:
    def __init__(self):
        self.longitude = None
        self.latitude = None
        self.altitude = None
        self.azimuth = None

    def update_telemetry(self, data):
        self.latitude = float(data[0])
        self.longitude = float(data[1])
        self.altitude = float(data[2])
        self.azimuth = float(data[3])

        """self.latitude = 52.085234
        self.longitude = 18.869299
        self.altitude = 15
        self.azimuth = 280"""

    def update_telemetry_manually(self, longitude, latitude, altitude, azimuth):
        self.longitude = longitude
        self.latitude = latitude
        self.altitude = altitude
        self.azimuth = azimuth

    def to_string(self):
        return "{:.7f},{:.7f}".format(self.latitude, self.longitude) + "," + str(self.altitude) + "," + str(self.azimuth)
        #print("lat", self.latitude, "lon", self.longitude, "alt", self.altitude, "azi", self.azimuth)