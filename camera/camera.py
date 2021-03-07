import cv2
from settings.settings import Values


class Camera:
    def __init__(self):
        self.camera = cv2.VideoCapture(Values.CAMERA)

    def get_frame(self):
        ret, frame = self.camera.read()
        if ret:
            return frame
        else:
            return None

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