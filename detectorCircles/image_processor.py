import cv2
import numpy as np
from settings.settings import Values


class ImageProcessor:

    @staticmethod
    def to_hsv(image: np.array):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        return hsv

    @staticmethod
    def detect_edges(image: np.array):
        edges = cv2.Canny(image, 30, 150)

        return edges

    @staticmethod
    def find_contours(image: np.array):
        cts, h = cv2.findContours(image, cv2.RETR_LIST,
                                  cv2.CHAIN_APPROX_SIMPLE)
        return cts

    @staticmethod
    def draw_contours(image: np.array, contours: np.array):
        image = cv2.drawContours(image, contours, -1,
                                 (0, 0, 255), thickness=3)
        return image

    @staticmethod
    def filter_contours_by_area(contours):
        output_contours = []
        for contour in contours:
            if cv2.contourArea(contour) > Values.MIN_AREA:
                output_contours.append(contour)
        return output_contours
