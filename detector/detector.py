import cv2
import numpy as np
from detector.image_processor import ImageProcessor
from detector.detections.detections import Detection
from settings.settings import Values
from scipy.spatial import distance


class Detector(ImageProcessor):

    def __init__(self):
        pass

    def extract_contours(self, image: np.array) -> np.array:
        hsv = self.to_hsv(image)

        hsv_brown_low = np.uint8([0, 35, 137])
        hsv_brown_high = np.uint8([37, 255, 255])

        hsv_white_low = np.uint8([49, 16, 148])
        hsv_white_high = np.uint8([102, 125, 215])

        hsv_white2_low = np.uint8([0, 0, 200])
        hsv_white2_high = np.uint8([255, 255, 255])

        mask1 = cv2.inRange(hsv, hsv_brown_low, hsv_brown_high)
        mask2 = cv2.inRange(hsv, hsv_white_low, hsv_white_high)
        mask3 = cv2.inRange(hsv, hsv_white2_low, hsv_white2_high)

        size = 3
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (size, size))
        masks = [mask1, mask2, mask3]

        contours_all_masks = []

        for mask in masks:
            post_process = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            contours = self.find_contours(post_process)
            [contours_all_masks.append(c) for c in contours]

        contours_all_masks = self.filter_contours_by_area(contours_all_masks)

        return contours_all_masks

    def detect(self, frame):

        height, width = frame.shape[:2]
        contours = self.extract_contours(frame)

        detections = []

        for cnt in contours:

            shape, points = self.get_contour_shape(cnt)

            if shape is not None:
                x, y, w, h = cv2.boundingRect(cnt)

                a = int(w / 3)

                rectangle = [x - Values.BOX_SIZE_INCREASE if x > Values.BOX_SIZE_INCREASE else x,
                             y - Values.BOX_SIZE_INCREASE if y > Values.BOX_SIZE_INCREASE else y,
                             w + 2 * Values.BOX_SIZE_INCREASE if w + 2 * Values.BOX_SIZE_INCREASE + x < width else w,
                             h + 2 * Values.BOX_SIZE_INCREASE if h + 2 * Values.BOX_SIZE_INCREASE + y < height else h]

                if shape != Values.TRIANGLE:
                    mid = (int(x + 0.5 * w), int(y + 0.5 * h))
                else:
                    mid = tuple(np.mean(points, axis=0, dtype=np.int))
                area = cv2.contourArea(cnt)

                frame_cut = frame[int(mid[1] - a / 2):int(mid[1] + a / 2), int(mid[0] - a / 2):int(mid[0] + a / 2)]

                G = frame_cut[:, :, 0]
                B = frame_cut[:, :, 1]
                R = frame_cut[:, :, 2]

                color = (np.median(G), np.median(B), np.median(R))

                detection = Detection(shape, rectangle, area, color, points, mid)
                detections.append(detection)

        return detections

    def get_contour_shape(self, contour):

        shape = None
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
        length = len(approx)
        points = []

        if cv2.isContourConvex(approx):
            if length == 3:

                for i in range(length):
                    points.append((approx[i][0][0], approx[i][0][1]))

                distances = [distance.euclidean(points[0], points[1]), distance.euclidean(points[0], points[2]),
                             distance.euclidean(points[1], points[2])]

                my_mean = np.mean(distances)

                wrong_size = False

                for ele in distances:
                    if abs(ele - my_mean) > 0.1 * my_mean:
                        wrong_size = True

                if not wrong_size:
                    shape = Values.TRIANGLE

            elif length == 4:

                for i in range(length):
                    points.append((approx[i][0][0], approx[i][0][1]))

                distances = [distance.euclidean(points[0], points[1]), distance.euclidean(points[0], points[2]),
                             distance.euclidean(points[0], points[3]), distance.euclidean(points[1], points[2]),
                             distance.euclidean(points[1], points[3]), distance.euclidean(points[2], points[3])]

                distances.sort()

                first_four = distances[:4]

                my_mean = np.mean(first_four)

                wrong_size = False

                for ele in first_four:
                    if abs(ele - my_mean) > 0.1 * my_mean:
                        wrong_size = True

                if not wrong_size:
                    shape = Values.SQUARE

            elif 7 < length < 23:
                shape = Values.CIRCLE

        return shape, points
