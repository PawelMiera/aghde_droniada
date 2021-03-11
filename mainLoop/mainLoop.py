from threading import Thread
from settings.settings import Values
from detector.detector import Detector
from camera.camera import CameraVideo
from telemetry.telemetry import Telemetry
from positionCalculator.positionCalculator import PositionCalculator
import cv2
import time


class MainLoop(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.camera = CameraVideo()
        self.detector = Detector()
        self.stop_loop = False
        self.telemetry = Telemetry()
        self.position_calculator = PositionCalculator()
        self.frame = cv2.imread("images/pole.png")

    def run(self):

        if Values.PRINT_FPS:
            last_time = time.time()
            ind = 0
        while True:
            try:
                if self.stop_loop:
                    break

                self.frame = cv2.imread("images/pole_new.jpg")
                # self.frame = self.camera.get_frame()

                self.frame = cv2.resize(self.frame, (Values.CAMERA_WIDTH, Values.CAMERA_HEIGHT))
                if self.frame is None:
                    continue

                detections = self.detector.detect(self.frame)
                self.telemetry.update_telemetry()
                self.position_calculator.update_meters_per_pixel(self.telemetry.altitude)
                self.position_calculator.calculate_max_meters_area()
                for d in detections:
                    lat, lon = self.position_calculator.calculate_point_lat_long(d.middle_point,
                                                                                 self.telemetry.latitude,
                                                                                 self.telemetry.longitude,
                                                                                 self.telemetry.azimuth)
                    d.update_lat_lon(lat, lon)
                    d.area_m = self.position_calculator.calculate_area_in_meters_2(d.area)
                    d.draw_detection(self.frame)

                cv2.imshow("frame", self.frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                if Values.PRINT_FPS:
                    ind += 1
                    if time.time() - last_time > 1:
                        print("FPS:", ind)
                        ind = 0
                        last_time = time.time()

            except Exception as e:
                print("Some error accrued: ", str(e))

    def close(self):
        self.stop_loop = True
