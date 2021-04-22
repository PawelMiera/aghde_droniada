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

        cv2.imshow("mask", mask_white + mask_orange + mask_brown + mask_brown_2)

        return contours_all_masks

    def detect(self, frame):

        contours = self.extract_contours(frame)

        detections = []

        for c in range(len(contours)):
            for cnt in contours[c]:

                area = cv2.contourArea(cnt)
                if area > Values.MIN_AREA:
                    bb = cv2.boundingRect(cnt)
                    shape, points = self.get_contour_shape(cnt, frame, bb)

                    if shape is not None:


                        if shape != Values.TRIANGLE:
                            mid = [int(bb[0] + 0.5 * bb[2]), int(bb[1] + 0.5 * bb[2])]
                        else:
                            mid = np.mean(points, axis=0, dtype=np.int)

                        area = cv2.contourArea(cnt)

                        detection_color = [0, 0, 0]
                        detection_color[c] += 1

                        detection = Detection(shape, bb, area, detection_color, points, mid)
                        detections.append(detection)

        return detections

    def get_contour_shape(self, contour, frame, bb):

        shape = None
        my_arclength = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * my_arclength, True)
        length = len(approx)
        points = []

        if cv2.isContourConvex(approx):
            if length == 3:

                for i in range(length):
                    points.append((approx[i][0][0], approx[i][0][1]))

                distances = [distance.euclidean(points[0], points[1]), distance.euclidean(points[0], points[2]),
                             distance.euclidean(points[1], points[2])]

                my_mean = np.mean(distances)

                differences = np.abs(np.subtract(distances, my_mean))

                sizes_check = np.greater(differences, 0.1 * my_mean)

                wrong_size = np.any(sizes_check)

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

                differences = np.abs(np.subtract(first_four, my_mean))

                sizes_check = np.greater(differences, 0.1 * my_mean)

                wrong_size = np.any(sizes_check)

                if not wrong_size:
                    shape = Values.SQUARE

            elif length >= 6:

                diff = int(bb[3] / 10)

                crop_coordinates_y = [bb[1] - diff, bb[1] + bb[3] + diff]
                crop_coordinates_x = [bb[0] - diff, bb[0] + bb[2] + diff]

                crop_coordinates_y = np.maximum(crop_coordinates_y, 0)
                crop_coordinates_x = np.maximum(crop_coordinates_x, 0)
                crop_coordinates_y = np.minimum(crop_coordinates_y, Values.CAMERA_HEIGHT)
                crop_coordinates_x = np.minimum(crop_coordinates_x, Values.CAMERA_WIDTH)

                crop = frame[crop_coordinates_y[0]:crop_coordinates_y[1], crop_coordinates_x[0]:crop_coordinates_x[1]]
                crop = cv2.resize(crop, (100, 100))
                crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

                circles = cv2.HoughCircles(crop, cv2.HOUGH_GRADIENT, 1, 50,
                                           param1=20, param2=27, minRadius=40, maxRadius=55)
                if circles is not None:
                    shape = Values.CIRCLE

                    """draw_crop = cv2.cvtColor(crop, cv2.COLOR_GRAY2BGR)
                    circles = np.uint16(np.around(circles))
                    for i in circles[0, :]:
                        center = (i[0], i[1])

                        cv2.circle(draw_crop, center, 1, (0, 100, 100), 3)

                        radius = i[2]
                        cv2.circle(draw_crop, center, radius, (255, 0, 255), 3)

                        cv2.imshow("draw crop", draw_crop)"""
        return shape, points
