import cv2
from settings.settings import Values
import numpy as np


class Detection:
    def __init__(self, shape, rectangle, area, color, points, mid):
        self.rectangle = rectangle
        self.shape = shape
        self.area = area
        self.color = color
        self.middle_point = mid
        self.points = points
        self.color_id = self.get_color_id()

    def get_color_id(self):
        color_distance = 1000
        color_id = None
        for i, col in enumerate(Values.COLORS):
            new_distance = np.sqrt(
                (col[0] - self.color[0]) ** 2 + (col[1] - self.color[1]) ** 2 + (col[2] - self.color[2]) ** 2)
            if new_distance < color_distance:
                color_id = i
                color_distance = new_distance

        return color_id

    def get_area_meters(self):
        pass

    def draw_detection(self, frame):
        for p in self.points:
            cv2.circle(frame, p, 5, (0, 0, 255), -1)

        if self.middle_point is not None:
            cv2.circle(frame, self.middle_point, 10, (0, 255, 0), -1)

        if self.rectangle is not None:
            x, y, w, h = self.rectangle
            x = x - Values.BOX_SIZE_INCREASE if x > Values.BOX_SIZE_INCREASE else x
            y = y - Values.BOX_SIZE_INCREASE if y > Values.BOX_SIZE_INCREASE else y
            w = w + 2 * Values.BOX_SIZE_INCREASE if w + 2 * Values.BOX_SIZE_INCREASE + x < Values.CAMERA_WIDTH else w
            h = h + 2 * Values.BOX_SIZE_INCREASE if h + 2 * Values.BOX_SIZE_INCREASE + y < Values.CAMERA_HEIGHT else h
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        label = ""

        if self.color_id is not None:
            if self.color_id == Values.ORANGE:
                label = "Orange "
            elif self.color_id == Values.BROWN:
                label = "Brown "
            elif self.color_id == Values.WHITE:
                label = "White "

        if self.shape is not None:
            if self.shape == Values.TRIANGLE:
                label += "Triangle"
            elif self.shape == Values.SQUARE:
                label += "Square"
            elif self.shape == Values.CIRCLE:
                label += "Circle"

            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)

            label_ymin = max(y, labelSize[1] + 10)

            cv2.rectangle(frame, (x, label_ymin - labelSize[1] - 10),
                          (x + labelSize[0], label_ymin + baseLine - 10), (255, 255, 255), cv2.FILLED)
            cv2.putText(frame, label, (x, label_ymin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
