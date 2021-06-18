from settings.settings import Values
import cv2


def get_frame_crop(frame, rectangle):
    if rectangle is not None:
        x, y, w, h = rectangle
        x1 = x - 2 * w
        y1 = y - 2 * h
        x2 = x + 3 * w
        y2 = y + 3 * h

        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(Values.CAMERA_WIDTH, x2)
        y2 = min(Values.CAMERA_HEIGHT, y2)
        crop = frame[y1:y2, x1:x2]
        crop = cv2.resize(crop, (400, 400))
        return crop


def my_distance(v, u):
    s = ((v[0]-u[0]) ** 2) + ((v[1]-u[1]) ** 2)
    return s ** 0.5
