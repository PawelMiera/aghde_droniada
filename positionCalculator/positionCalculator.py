import numpy as np
from settings.settings import Values


class PositionCalculator:

    def __init__(self):
        self.vertical_constant = self.calculate_vertical_constant()
        self.horizontal_constant = self.calculate_horizontal_constant()

    def calculate_vertical_constant(self):
        vertical_constant = 2 * np.math.tan(np.deg2rad(Values.VERTICAL_ANGLE / 2)) / Values.CAMERA_WIDTH
        return vertical_constant

    def calculate_horizontal_constant(self):
        horizontal_constant = 2 * np.math.tan(np.deg2rad(Values.HORIZONTAL_ANGLE / 2)) / Values.CAMERA_HEIGHT
        return horizontal_constant

    def px_2_meters_vertical(self, altitude):
        return self.vertical_constant * altitude

    def px_2_meters_horizontal(self, altitude):
        return self.horizontal_constant * altitude
