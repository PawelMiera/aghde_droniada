import cv2
import numpy as np
from detector.image_processor import ImageProcessor
from detector.detections.detections import Detection
from settings.settings import Values
from scipy.spatial import distance
import time


class Detector(ImageProcessor):

    def __init__(self):
        self.brown_low = (161, 26, 128)
        self.brown_high = (203, 73, 225)

        self.brown_low_2 = (0, 36, 128)
        self.brown_high_2 = (9, 75, 138)

        self.white_low = (65, 0, 230)
        self.white_high = (178, 81, 255)

        self.orange_low = (10, 35, 155)
        self.orange_high = (57, 114, 255)

    def extract_contours(self, image: np.array) -> np.array:
        hsv = self.to_hsv(image)

        mask_brown = cv2.inRange(hsv, self.brown_low, self.brown_high)
        mask_brown_2 = cv2.inRange(hsv, self.brown_low_2, self.brown_high_2)
        mask_white = cv2.inRange(hsv, self.white_low, self.white_high)
        mask_orange = cv2.inRange(hsv, self.orange_low, self.orange_high)

        #size = 3
        #kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (size, size))  # TO TEZ OUT

        cnt_white = self.find_contours(mask_white)
        cnt_orange = self.find_contours(mask_orange)
        cnt_brown = self.find_contours(mask_brown + mask_brown_2)

        contours_all_masks = [cnt_white, cnt_orange, cnt_brown]

        #cv2.imshow("mask", mask_white + mask_orange + mask_brown + mask_brown_2)

        return contours_all_masks

    def detect(self, frame):

        contours = self.extract_contours(frame)

        detections = []

        for c in range(len(contours)):
            for cnt in contours[c]:

                area = cv2.contourArea(cnt)
                if area > Values.MIN_AREA:
                    shape, points = self.get_contour_shape(cnt)

                    #img = frame.copy()
                    #cv2.drawContours(img, [cnt], 0, (0,255,0), 3)

                    if shape is not None:
                        x, y, w, h = cv2.boundingRect(cnt)

                        if shape != Values.TRIANGLE:
                            mid = [int(x + 0.5 * w), int(y + 0.5 * h)]
                        else:
                            mid = np.mean(points, axis=0, dtype=np.int)

                        area = cv2.contourArea(cnt)

                        detection_color = [0, 0, 0]
                        detection_color[c] += 1

                        detection = Detection(shape, [x, y, w, h], area, detection_color, points, mid)
                        detections.append(detection)


        """for cnt in contours:

            shape, points = self.get_contour_shape(cnt)

            if shape is not None:
                x, y, w, h = cv2.boundingRect(cnt)

                a = int(w / 3)

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

                detection = Detection(shape, [x, y, w, h], area, color, points, mid)
                detections.append(detection)"""

        return detections

    def get_contour_shape(self, contour):

        shape = None
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
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

            elif 7 <= length < 23:
                shape = Values.CIRCLE

        return shape, points
