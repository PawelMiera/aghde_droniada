import numpy as np
from settings.settings import Values
from geographiclib.geodesic import Geodesic
import cv2
from telemetry.telemetry import Telemetry


class PositionCalculator:

    def __init__(self, telemetry: Telemetry):
        self.vertical_constant = self.calculate_vertical_constant()
        self.horizontal_constant = self.calculate_horizontal_constant()
        self.meters_per_pixel_vertical = None
        self.meters_per_pixel_horizontal = None
        self.max_meters_vertical = None
        self.max_meters_horizontal = None
        self.max_meters_area = None
        self.geod = Geodesic.WGS84
        self.point_lu = None
        self.point_ld = None
        self.point_ru = None
        self.point_rd = None
        self.line_u = None
        self.line_d = None
        self.line_l = None
        self.line_r = None
        self.distance_vertical_geo = None
        self.distance_horizontal_geo = None
        self.telemetry = telemetry

    def calculate_vertical_constant(self):
        vertical_constant = 2 * np.math.tan(np.deg2rad(Values.VERTICAL_ANGLE / 2)) / Values.CAMERA_WIDTH
        return vertical_constant

    def calculate_horizontal_constant(self):
        horizontal_constant = 2 * np.math.tan(np.deg2rad(Values.HORIZONTAL_ANGLE / 2)) / Values.CAMERA_HEIGHT
        return horizontal_constant

    def update_meters_per_pixel(self):
        self.meters_per_pixel_vertical = self.calculate_meters_per_pixel_vertical(self.telemetry.altitude)
        self.meters_per_pixel_horizontal = self.calculate_meters_per_pixel_horizontal(self.telemetry.altitude)

    def calculate_meters_per_pixel_vertical(self, altitude):
        return self.vertical_constant * altitude

    def calculate_meters_per_pixel_horizontal(self, altitude):
        return self.horizontal_constant * altitude

    def calculate_max_meters_horizontal(self):
        """
        Need to run calculate_meters_per_pixel_horizontal() first!!!
        """
        self.max_meters_horizontal = self.meters_per_pixel_horizontal * Values.CAMERA_HEIGHT

    def calculate_max_meters_vertical(self):
        """
        Need to run calculate_meters_per_pixel_horizontal() first!!!
        """
        self.max_meters_vertical = self.meters_per_pixel_vertical * Values.CAMERA_WIDTH

    def calculate_max_meters_area(self):
        """
        Need to run calculate_meters_per_pixel_vertical() and calculate_meters_per_pixel_horizontal() first!!!
        """
        self.calculate_max_meters_vertical()
        self.calculate_max_meters_horizontal()
        self.max_meters_area = self.max_meters_vertical * self.max_meters_horizontal

    def calculate_extreme_points(self, latitude, longitude, azimuth):
        """
        Need to run calculate_max_meters_horizontal() and calculate_max_meters_vertical() first!!!
        """
        distance = np.sqrt(((self.max_meters_horizontal / 2) ** 2) + ((self.max_meters_vertical / 2) ** 2))
        b = np.rad2deg(np.math.atan(Values.CAMERA_WIDTH / Values.CAMERA_HEIGHT))

        a1 = azimuth - b
        a2 = azimuth - 180 + b
        a3 = azimuth + b
        a4 = azimuth + 180 - b

        print("{:.8f},{:.8f}".format(latitude, longitude))

        g = self.geod.Direct(latitude, longitude, a1, distance)
        self.point_lu = [g['lat2'], g['lon2']]
        print("{:.8f},{:.8f}".format(g['lat2'], g['lon2']))

        g = self.geod.Direct(latitude, longitude, a2, distance)
        self.point_ld = [g['lat2'], g['lon2']]
        print("{:.8f},{:.8f}".format(g['lat2'], g['lon2']))

        g = self.geod.Direct(latitude, longitude, a3, distance)
        self.point_ru = [g['lat2'], g['lon2']]
        print("{:.8f},{:.8f}".format(g['lat2'], g['lon2']))

        g = self.geod.Direct(latitude, longitude, a4, distance)
        self.point_rd = [g['lat2'], g['lon2']]
        print("{:.8f},{:.8f}".format(g['lat2'], g['lon2']))

        self.line_u = self.get_line_factors(self.point_lu, self.point_ru)
        self.line_d = self.get_line_factors(self.point_ld, self.point_rd)
        self.line_l = self.get_line_factors(self.point_lu, self.point_ld)
        self.line_r = self.get_line_factors(self.point_ru, self.point_rd)

        """print(str(l1[0]) + "*x + " + str(l1[1]) + "*y +" + str(l1[2]) + "= 0")
        print(str(l2[0]) + "*x + " + str(l2[1]) + "*y +" + str(l2[2]) + "= 0")
        print(str(l3[0]) + "*x + " + str(l3[1]) + "*y +" + str(l3[2]) + "= 0")
        print(str(l4[0]) + "*x + " + str(l4[1]) + "*y +" + str(l4[2]) + "= 0")"""
        self.distance_vertical_geo = self.calculate_point_to_line_distance(self.point_lu, self.line_r)
        self.distance_horizontal_geo = self.calculate_point_to_line_distance(self.point_lu, self.line_d)

    def get_detection_on_image_cords(self, lat, long):
        """
        Need to run calculate_extreme_points() first!!!
        """
        p = [lat, long]
        du = self.calculate_point_to_line_distance(p, self.line_u)
        dd = self.calculate_point_to_line_distance(p, self.line_d)
        dl = self.calculate_point_to_line_distance(p, self.line_l)
        dr = self.calculate_point_to_line_distance(p, self.line_r)

        h = self.distance_horizontal_geo
        v = self.distance_vertical_geo

        if du <= h and dd <= h and dl <= v and dr <= v:
            x = dl / v
            y = du / h
            x *= Values.CAMERA_WIDTH
            y *= Values.CAMERA_HEIGHT
            return int(x), int(y)
        else:
            return None

    def calculate_point_to_line_distance(self, p, l):
        distance = abs(l[0] * p[0] + l[1] * p[1] + l[2])
        distance /= np.sqrt((l[0] ** 2) + (l[1] ** 2))
        return distance

    def get_line_factors(self, p1, p2):
        a = p1[1] - p2[1]
        b = p2[0] - p1[0]
        c = p1[0] * p2[1] - p2[0] * p1[1]
        return [a, b, c]

    def calculate_point_lat_long(self, point):

        p = point.copy()
        p[0] -= Values.CAMERA_WIDTH / 2
        p[1] = Values.CAMERA_HEIGHT / 2 - p[1]

        angle = np.rad2deg(np.math.atan2(p[0], p[1]))

        end_angle = self.telemetry.azimuth + angle

        p[0] *= self.meters_per_pixel_vertical
        p[1] *= self.meters_per_pixel_horizontal

        distance = np.sqrt(np.sum(np.square(p)))

        g = self.geod.Direct(self.telemetry.latitude, self.telemetry.longitude, end_angle, distance)

        return g['lat2'], g['lon2']

    def transfrom_point_by_angle(self, x, y, azimuth_radians):
        x_1 = x * np.math.cos(azimuth_radians) - y * np.math.sin(azimuth_radians)
        y_1 = x * np.math.sin(azimuth_radians) + y * np.math.cos(azimuth_radians)
        return x_1, y_1

    def calculate_area_in_meters_2(self, area):
        area_m = area * self.max_meters_area / Values.MAX_PIXEL_AREA
        return area_m


if __name__ == '__main__':
    # print(np.rad2deg(np.math.atan(1 / 2)))

    test = PositionCalculator()
    test.update_meters_per_pixel(20)
    test.calculate_max_meters_area()
    test.calculate_extreme_points(51.085234, 19.869299, 90)
    p = test.get_detection_on_image_cords(51.08516100, 19.86929900)
    print(p)
    frame = cv2.imread("pole_new.jpg")
    cv2.circle(frame, p, 5, (0, 0, 255), -1)
    cv2.imshow("test", frame)
    cv2.waitKey(0)
    # test.calculate_point_lat_long([100, 440], 51.085234, 19.869299, 0)
    # x1, y1 = test.transfrom_point_by_angle(2, 1, np.deg2rad(45))
    # print(x1, y1)
