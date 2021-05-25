from threading import Thread
from settings.settings import Values
from detector.detector import Detector
from camera.camera import Camera
from telemetryThread.telemetry import TelemetryThread
from positionCalculator.positionCalculator import PositionCalculator
import cv2
import time
import traceback
import os
import csv


class MainLoop(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.camera = Camera()
        self.detector = Detector()
        self.stop_loop = False
        self.telemetry = TelemetryThread()
        self.position_calculator = PositionCalculator(self.telemetry)
        self.frame = None
        self.all_detections = []
        self.confirmed_detections = []
        self.confirmed_detection_id = 0

    def run(self):

        time_index = 0

        self.id = 1820

        with open('C:/Users/Pawel/Desktop/0/telemetry.txt') as f:
            reader = csv.reader(f)
            data = list(reader)

        if Values.PRINT_FPS:
            last_time = time.time()
            ind = 0
        while True:
            try:
                if self.stop_loop:
                    break

                #path = "images/" + str(1) + ".jpg"
                #path = "images/a" + str(self.id) + ".jpg"
                path = "C:/Users/Pawel/Desktop/0/images/" + str(self.id) + ".jpg"

                self.frame = cv2.imread(path)
                #self.frame = self.camera.get_frame()

                if self.frame is None:
                    continue

                self.frame = cv2.resize(self.frame, (Values.CAMERA_WIDTH, Values.CAMERA_HEIGHT))

                detections = self.detector.detect(self.frame)
                self.telemetry.update_telemetry(data[self.id])

                self.telemetry.to_string()

                self.position_calculator.update_meters_per_pixel()
                self.position_calculator.calculate_max_meters_area()
                self.position_calculator.calculate_extreme_points()     # tylko potrzebne zeby wyswietlic stare wykrycia

                for d in detections:
                    lat, lon = self.position_calculator.calculate_point_lat_long(d.middle_point)
                    d.update_lat_lon(lat, lon)
                    d.area_m = self.position_calculator.calculate_area_in_meters_2(d.area)
                    d.draw_detection(self.frame)

                    for conf_d in self.confirmed_detections:
                        if d.check_detection(conf_d):
                            conf_d += d
                            conf_d.last_seen = time_index
                            d.to_delete = True
                            break
                    if d.to_delete:
                        continue

                    for all_d in self.all_detections:
                        if d.check_detection(all_d):
                            all_d += d
                            all_d.last_seen = time_index
                            d.to_delete = True
                            break
                    if not d.to_delete:
                        d.last_seen = time_index
                        self.all_detections.append(d)

                for all_d in self.all_detections:
                    if all_d.seen_times > 20:
                        all_d.detection_id = self.confirmed_detection_id
                        self.confirmed_detection_id += 1
                        filename = os.path.join(os.path.join(os.getcwd(), "saved_detection_images"),
                                                str(all_d.detection_id) + ".jpg")
                        self.save_frame_crop(all_d.rectangle, filename)
                        self.confirmed_detections.append(all_d)
                        all_d.to_delete = True
                    elif all_d.seen_times > 8:
                        if time_index - all_d.last_seen > 800:
                            all_d.to_delete = True
                    else:
                        if time_index - all_d.last_seen > 20:
                            all_d.to_delete = True

                self.all_detections = list(filter(lambda x: not x.to_delete, self.all_detections))  # do sprawdzenia

                for conf_d in self.confirmed_detections:
                    conf_d.draw_confirmed_detection(self.frame, self.position_calculator)

                cv2.imshow("frame", self.frame)

                time_index += 1
                self.id += 1
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                if Values.PRINT_FPS:
                    ind += 1
                    if time.time() - last_time > 1:
                        print("FPS:", ind)
                        ind = 0
                        last_time = time.time()

            except Exception:
                print("Some error accrued: ")
                traceback.print_exc()
        self.close()

    def save_frame_crop(self, rectangle, filename):
        if rectangle is not None:
            x, y, w, h = rectangle
            x1 = x - w
            y1 = y-h
            x2 = x + 2 * w
            y2 = y + 2 * h

            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(Values.CAMERA_WIDTH, x2)
            y2 = min(Values.CAMERA_HEIGHT, y2)
            crop = self.frame[y1:y2, x1:x2]
            crop = cv2.resize(crop, (400, 400))
            cv2.imwrite(filename, crop)

    def close(self):
        self.camera.close()
        self.stop_loop = True
