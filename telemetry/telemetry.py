

class Telemetry:
    def __init__(self):
        self.longitude = None
        self.latitude = None
        self.altitude = None
        self.azimuth = None

    def update_telemetry(self):
        pass

    def update_telemetry_manually(self, longitude, latitude, altitude, azimuth):
        self.longitude = longitude
        self.latitude = latitude
        self.altitude = altitude
        self.azimuth = azimuth