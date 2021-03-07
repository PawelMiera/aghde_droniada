from threading import Thread
from settings.settings import Values
from detector.detector import Detector
from camera.camera import CameraVideo
import cv2
import time


class MainLoop(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.camera = CameraVideo()
        self.detector = Detector()
        self.stop_loop = False
        self.frame = cv2.imread("images/pole.png")

    def run(self):
        try:
            if Values.PRINT_FPS:
                last_time = time.time()
                ind = 0
            while True:
                if self.stop_loop:
                    break

                #self.frame = cv2.imread("images/pole.png")
                self.frame = self.camera.get_frame()

                if self.frame is None:
                    continue

                detections = self.detector.detect(self.frame)

                for d in detections:
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

        except ValueError as er:
            print("Some error accured: ", str(er))
        except KeyboardInterrupt:
            print("Closing")
        finally:
            self.camera.close()

    def close(self):
        self.stop_loop = True
