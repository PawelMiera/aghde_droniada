from threading import Thread
from settings.settings import Values
from detector.detector import Detector
from camera.camera import Camera
from telemetry.telemetry import Telemetry
from positionCalculator.positionCalculator import PositionCalculator
import cv2
import time
import traceback


class MainLoop(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.camera = Camera()
        self.detector = Detector()
        self.stop_loop = False
        self.telemetry = Telemetry()
        self.position_calculator = PositionCalculator(self.telemetry)
        self.frame = None
        self.all_detections = []
        self.confirmed_detections = []
        self.confirmed_detection_id = 0

    def run(self):

        self.id = 1

        time_index = 0

        if Values.PRINT_FPS:
            last_time = time.time()
            ind = 0
        while True:
            try:
                if self.stop_loop:
                    break

                path = "tests/to train/" + str(self.id) + ".jpg"

                self.frame = cv2.imread("images/" + str(self.id) + ".jpg")
                # self.frame = self.camera.get_frame()

                if self.frame is None:
                    continue

                self.frame = cv2.resize(self.frame, (Values.CAMERA_WIDTH, Values.CAMERA_HEIGHT))

                detections = self.detector.detect(self.frame)
                self.telemetry.update_telemetry()  # prawdopodobnie automatycznie !
                self.position_calculator.update_meters_per_pixel()
                self.position_calculator.calculate_max_meters_area()

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

                for d in detections:
                    if not d.to_delete:
                        self.all_detections.append(d)

                for all_d in self.all_detections:
                    if all_d.seen_times > 8:
                        self.confirmed_detections.append(all_d)
                        all_d.to_delete = True
                    elif all_d.seen_times > 4:
                        if time_index - all_d.last_seen > 800:
                            all_d.to_delete = True
                    else:
                        if time_index - all_d.last_seen > 20:
                            all_d.to_delete = True

                self.all_detections = list(filter(lambda x: not x.to_delete, self.all_detections))  # do sprawdzenia

                cv2.imshow("frame", self.frame)

                time_index += 1
                self.id += 1
                if cv2.waitKey(0) & 0xFF == ord('q'):
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

    def close(self):
        self.camera.close()
        self.stop_loop = True
