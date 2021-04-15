import cv2
from settings.settings import Values
import numpy as np


class Detection:
    def __init__(self, shape, rectangle, area, color, points, mid):
        self.rectangle = rectangle
        self.shape = shape
        self.area = area
        self.area_m = None
        self.latitude = None
        self.longitude = None
        self.color = color
        self.middle_point = mid
        self.points = points
        self.color_id = np.argmax(self.color)
        self.detection_id = None
        self.to_delete = False
        self.last_seen = 0
        self.seen_times = 1

    def update_color_id(self):
        self.color_id = np.argmax(self.color)

    def get_color_id(self):  # raczej do wywalenia :)
        color_distance = 1000
        color_id = None
        for i, col in enumerate(Values.COLORS):
            new_distance = np.sqrt(
                (col[0] - self.color[0]) ** 2 + (col[1] - self.color[1]) ** 2 + (col[2] - self.color[2]) ** 2)
            if new_distance < color_distance:
                color_id = i
                color_distance = new_distance

        return color_id

    def update_lat_lon(self, lat, lon):
        self.latitude = lat
        self.longitude = lon

    def get_area_meters(self):
        pass

    def __add__(self, other):
        self.color = np.add(other.color, self.color)
        self.update_color_id()
        self.seen_times += 1
        self.area_m = (self.area_m * (self.seen_times - 1) + other.area_m) / self.seen_times
        self.latitude = (self.latitude * (self.seen_times - 1) + other.latitude) / self.seen_times
        self.longitude = (self.longitude * (self.seen_times - 1) + other.longitude) / self.seen_times
        return self

    def check_detection(self, new_det):

        # mozna dodac sprawdzanie koloru
        return self.shape == new_det.shape and abs(self.latitude - new_det.latitude) < Values.MAX_LONG_LAT_DIFF \
               and abs(self.longitude - new_det.longitude) < Values.MAX_LONG_LAT_DIFF \
               and abs(self.area_m - new_det.area_m) < Values.MAX_AREA_DIFF

    def draw_detection(self, frame):
        for p in self.points:
            cv2.circle(frame, p, 5, (0, 0, 255), -1)

        if self.middle_point is not None:
            cv2.circle(frame, tuple(self.middle_point), 10, (0, 255, 0), -1)

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
        labels = [label]
        if self.latitude is not None and self.longitude is not None:
            labels.append("Lat: " + '%.5f' % self.latitude)
            labels.append("Lon: " + '%.5f' % self.longitude)
        if self.area_m is not None:
            labels.append("Area: " + '%.2f' % self.area_m)

        labelSizes_x = []
        labelSizes_y = []
        for l in labels:
            labelSize, baseLine = cv2.getTextSize(l, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            labelSizes_x.append(labelSize[0])
            labelSizes_y.append(labelSize[1])

        rect_y_min = y - (labelSize[1] + 10) * len(labels)
        rect_y_min = max(0, rect_y_min)

        label_ymin = max(y, max(labelSizes_y) + 10, 0)

        max_x = max(labelSizes_x)

        cv2.rectangle(frame, (x, rect_y_min),
                      (x + max_x, label_ymin + baseLine - 10), (255, 255, 255), cv2.FILLED)
        for l in labels:
            cv2.putText(frame, l, (x, rect_y_min + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            rect_y_min += 20

        """labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        label_ymin = max(y, labelSize[1] + 10)

        cv2.rectangle(frame, (x, label_ymin - labelSize[1] - 10 * len(labels)),
                      (x + labelSize[0], label_ymin + baseLine - 10), (255, 255, 255), cv2.FILLED)

        cv2.putText(frame, label, (x, label_ymin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        """
