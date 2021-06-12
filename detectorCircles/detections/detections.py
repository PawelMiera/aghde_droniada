import cv2
from settings.settings import Values
import numpy as np


class Detection:
    def __init__(self, rectangle, color, mid):
        self.rectangle = rectangle
        self.latitude = None
        self.longitude = None
        self.color = color
        self.middle_point = mid
        self.color_id = np.argmax(self.color)
        self.detection_id = None
        self.to_delete = False
        self.last_seen = 0
        self.seen_times = 1
        self.filename = ""
        self.update_firebase_detection = False
        self.firebase_path = ""

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
        self.latitude = (self.latitude * (self.seen_times - 1) + other.latitude) / self.seen_times
        self.longitude = (self.longitude * (self.seen_times - 1) + other.longitude) / self.seen_times
        return self

    def check_detection(self, new_det):

        # mozna dodac sprawdzanie koloru
        return abs(self.latitude - new_det.latitude) < Values.MAX_LONG_LAT_DIFF \
               and abs(self.longitude - new_det.longitude) < Values.MAX_LONG_LAT_DIFF

    def get_description(self):
        label = ""
        if self.color_id is not None:
            if self.color_id == Values.ORANGE:
                label = "Orange "
            elif self.color_id == Values.BROWN:
                label = "Brown "
            elif self.color_id == Values.WHITE:
                label = "White "

            label += "Circle"

        return label

    def draw_detection(self, frame):

        if self.middle_point is not None:
            cv2.circle(frame, tuple(self.middle_point), 10, (0, 255, 0), -1)

        labels = [self.get_description()]
        if self.latitude is not None and self.longitude is not None:
            labels.append("Lat: " + '%.5f' % self.latitude)
            labels.append("Lon: " + '%.5f' % self.longitude)

        if self.rectangle is not None:
            x, y, w, h = self.rectangle
            x = max(0, x - Values.BOX_SIZE_INCREASE)
            y = max(0, y - Values.BOX_SIZE_INCREASE)
            x1 = min(Values.CAMERA_WIDTH, x + w + 2 * Values.BOX_SIZE_INCREASE)
            y1 = min(Values.CAMERA_HEIGHT, y + h + 2 * Values.BOX_SIZE_INCREASE)

            cv2.rectangle(frame, (x, y), (x1, y1), (255, 0, 0), 2)

            labelSizes_x = []
            labelSizes_y = []
            for l in labels:
                labelSize, baseLine = cv2.getTextSize(l, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                labelSizes_x.append(labelSize[0])
                labelSizes_y.append(labelSize[1])

            height = (max(labelSizes_y) + 9) * len(labels)
            rect_y_min = y - height

            if y < height:
                rect_y_min = y1

            max_x = max(labelSizes_x)

            cv2.rectangle(frame, (x, rect_y_min),
                          (x + max_x, rect_y_min + height), (255, 255, 255), cv2.FILLED)
            for l in labels:
                cv2.putText(frame, l, (x, rect_y_min + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                rect_y_min += 20

    def draw_confirmed_detection(self, frame, my_mid):
        cv2.circle(frame, my_mid, 22, (0, 0, 255), 3)

    def getString(self):
        label = ""

        if self.color_id is not None:
            if self.color_id == Values.ORANGE:
                label = "Orange,"
            elif self.color_id == Values.WHITE:
                label = "White,"
            elif self.color_id == Values.BROWN:
                label = "Brown,"

        label += "Circle,"
        label += str(self.latitude) + ","
        label += str(self.longitude) + ","
        label += str(self.seen_times) + ","
        label += str(self.filename) + "\n"
        return label
