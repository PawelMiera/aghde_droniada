import cv2
from settings.settings import Values
import VideoCapture
import numpy as np

class Camera:
    def __init__(self):
        self.camera = cv2.VideoCapture(self.gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)

    def get_frame(self):
        if self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                return frame
            else:
                return None

    def gstreamer_pipeline(self,
                           capture_width=1280,
                           capture_height=720,
                           display_width=1280,
                           display_height=720,
                           framerate=60,
                           flip_method=0,
                           ):
        return (
                "nvarguscamerasrc ! "
                "video/x-raw(memory:NVMM), "
                "width=(int)%d, height=(int)%d, "
                "format=(string)NV12, framerate=(fraction)%d/1 ! "
                "nvvidconv flip-method=%d ! "
                "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
                "videoconvert ! "
                "video/x-raw, format=(string)BGR ! appsink max-buffers=1 drop=True"
                % (
                    capture_width,
                    capture_height,
                    framerate,
                    flip_method,
                    display_width,
                    display_height,
                )
        )

    def close(self):
        self.camera.release()
        cv2.destroyAllWindows()


class CameraVideo:
    def __init__(self):
        self.camera = cv2.VideoCapture('images/1.MP4')

    def get_frame(self):
        ret, frame = self.camera.read()
        if ret:
            return frame
        else:
            return None

    def close(self):
        self.camera.release()
        cv2.destroyAllWindows()


class BasicCamera:
    def __init__(self):

        self.camera = VideoCapture.Device(devnum=Values.CAMERA, showVideoWindow=0)
        #self.camera.setResolution(1280, 720)

        #self.camera = cv2.VideoCapture(1, cv2.CAP_MSMF)
        #self.camera.set(50, 0)
        #self.camera.set(3, 1280)
        #self.camera.set(4, 720)                     # moze zakomentowac ??

    def get_frame(self):
        buff = self.camera.getBuffer()
        self.camera.getImage()
        frame = np.frombuffer(buff[0], np.uint8).reshape(buff[2], buff[1], 3)
        flipVertical = cv2.flip(cv2.resize(frame, (1280, 720)), 0)
        return flipVertical

    def close(self):
        cv2.destroyAllWindows()


class BasicCamera2:
    def __init__(self):

        #self.camera = VideoCapture.Device(devnum=Values.CAMERA, showVideoWindow=0)
        #self.camera.setResolution(1280, 720)

        self.camera = cv2.VideoCapture(Values.CAMERA)
        self.camera.set(3, 1280)
        self.camera.set(4, 720)                     # moze zakomentowac ??

    def get_frame(self):
        ret, frame = self.camera.read()
        return frame

    def close(self):
        cv2.destroyAllWindows()