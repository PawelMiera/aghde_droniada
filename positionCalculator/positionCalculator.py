import numpy as np
from settings.settings import Values
from geographiclib.geodesic import Geodesic


class PositionCalculator:

    def __init__(self):
        self.vertical_constant = self.calculate_vertical_constant()
        self.horizontal_constant = self.calculate_horizontal_constant()
        self.meters_per_pixel_vertical = None
        self.meters_per_pixel_horizontal = None
        self.geod = Geodesic.WGS84

    def update_meters_per_pixel(self, altitude):
        self.meters_per_pixel_vertical = self.calculate_meters_per_pixel_vertical(altitude)
        self.meters_per_pixel_horizontal = self.calculate_meters_per_pixel_horizontal(altitude)

    def calculate_vertical_constant(self):
        vertical_constant = 2 * np.math.tan(np.deg2rad(Values.VERTICAL_ANGLE / 2)) / Values.CAMERA_WIDTH
        return vertical_constant

    def calculate_horizontal_constant(self):
        horizontal_constant = 2 * np.math.tan(np.deg2rad(Values.HORIZONTAL_ANGLE / 2)) / Values.CAMERA_HEIGHT
        return horizontal_constant

    def calculate_meters_per_pixel_vertical(self, altitude):
        return self.vertical_constant * altitude

    def calculate_meters_per_pixel_horizontal(self, altitude):
        return self.horizontal_constant * altitude

    def get_max_meters_horizontal(self):
        return self.meters_per_pixel_horizontal * Values.CAMERA_HEIGHT

    def get_max_meters_vertical(self):
        return self.meters_per_pixel_vertical * Values.CAMERA_WIDTH

    def calculate_extreme_points(self, latitude, longitude, azimuth):
        distance = np.sqrt(((self.get_max_meters_horizontal()/2) ** 2) + ((self.get_max_meters_vertical()/2) ** 2))
        b = np.rad2deg(np.math.atan(Values.CAMERA_WIDTH / Values.CAMERA_HEIGHT))
        a1 = azimuth - b
        a2 = azimuth - 180 + b
        a3 = azimuth + b
        a4 = azimuth + 180 - b
        print("{:.8f},{:.8f}".format(latitude, longitude))
        g = self.geod.Direct(latitude, longitude, a1, distance)
        print("{:.8f},{:.8f}".format(g['lat2'], g['lon2']))
        g = self.geod.Direct(latitude, longitude, a2, distance)
        print("{:.8f},{:.8f}".format(g['lat2'], g['lon2']))
        g = self.geod.Direct(latitude, longitude, a3, distance)
        print("{:.8f},{:.8f}".format(g['lat2'], g['lon2']))
        g = self.geod.Direct(latitude, longitude, a4, distance)
        print("{:.8f},{:.8f}".format(g['lat2'], g['lon2']))

    def calculate_point_lat_long(self, x, y, latitude, longitude, azimuth):
        x1 = x - Values.CAMERA_WIDTH / 2
        y1 = Values.CAMERA_HEIGHT / 2 - y

        angle = np.rad2deg(np.math.atan2(x1, y1))

        end_angle = azimuth + angle

        distance = np.sqrt(((x1 * self.meters_per_pixel_vertical) ** 2) + ((y1 * self.meters_per_pixel_horizontal) ** 2))

        g = self.geod.Direct(latitude, longitude, end_angle, distance)
        print("{:.8f},{:.8f}".format(g['lat2'], g['lon2']))

    def transfrom_point_by_angle(self, x, y, azimuth_radians):
        x_1 = x * np.math.cos(azimuth_radians) - y * np.math.sin(azimuth_radians)
        y_1 = x * np.math.sin(azimuth_radians) + y * np.math.cos(azimuth_radians)
        return x_1, y_1


if __name__ == '__main__':

    #print(np.rad2deg(np.math.atan(1 / 2)))

    test = PositionCalculator()
    test.update_meters_per_pixel(30)
    test.calculate_extreme_points(51.085234, 19.869299, 185)
    test.calculate_point_lat_long(100, 440, 51.085234, 19.869299, 185)
    test.calculate_point_lat_long2(100, 440, 51.085234, 19.869299, 185)
    #x1, y1 = test.transfrom_point_by_angle(2, 1, np.deg2rad(45))
    #print(x1, y1)