import cv2
import numpy as np
from detector.image_processor import ImageProcessor
from detectorCircles.detections.detections import Detection
from settings.settings import Values
import time


class CircleDetector(ImageProcessor):

    def __init__(self):

        self.brown_low = (0, 73, 141)
        self.brown_high = (18, 165, 209)

        self.orange_low = (13, 109, 217)
        self.orange_high = (29, 187, 255)

        self.white_low = (0, 0, 235)
        self.white_high = (168, 43, 255)

        self.last_color_update = 0

    def update_color_ranges(self, hsv):
        val = np.median(hsv[:, :, 2])

        if val < 14:
            self.white_low = (0, 0, 170)
            self.white_high = (190, 94, 255)
            self.orange_low = (0, 146, 130)
            self.orange_high = (50, 229, 222)
            self.brown_low = (0, 35, 100)
            self.brown_high = (33, 168, 160)

        elif 14 <= val < 25:
            self.white_low = (0, 0, 210)
            self.white_high = (190, 40, 255)
            self.orange_low = (0, 146, 176)
            self.orange_high = (50, 209, 222)
            self.brown_low = (0, 35, 100)
            self.brown_high = (33, 168, 160)

        elif 25 <= val < 38:
            self.white_low = (0, 0, 210)
            self.white_high = (190, 40, 255)
            self.orange_low = (9, 128, 215)
            self.orange_high = (21, 195, 255)    #s179
            self.brown_low = (0, 45, 164)        #s87
            self.brown_high = (25, 151, 208)        #h21

        elif 38 <= val < 48:
            self.white_low = (0, 0, 210)
            self.white_high = (190, 40, 255)
            self.orange_low = (0, 135, 225)
            self.orange_high = (51, 195, 255)
            self.brown_low = (0, 66, 142)            ## v187 s83
            self.brown_high = (34, 159, 240)         ## v210  v230(9)

        elif 48 <= val < 58:
            self.white_low = (0, 0, 210)
            self.white_high = (190, 40, 255)
            self.orange_low = (0, 132, 200)          ### s124 v194  s132(4)
            self.orange_high = (51, 220, 255)        ## s 199
            self.brown_low = (0, 39, 160)        ## v150     #169
            self.brown_high = (35, 148, 242)     ## v216

        elif 58 <= val < 65:
            self.white_low = (0, 0, 210)
            self.white_high = (190, 40, 255)
            self.orange_low = (0, 144, 212)      #168
            self.orange_high = (50, 228, 255)
            self.brown_low = (0, 65, 154)           #s92         #sprawdz braz
            self.brown_high = (20, 147, 220)         #v198

        elif 65 <= val < 73:
            self.white_low = (0, 0, 210)
            self.white_high = (190, 40, 255)
            self.orange_low = (0, 110, 224)      #s110
            self.orange_high = (52, 214, 255)    #s 172
            self.brown_low = (0, 46, 175)
            self.brown_high = (198, 91, 243)     #v235

        else:
            self.white_low = (0, 0, 210)
            self.white_high = (190, 40, 255)
            self.orange_low = (0, 99, 225)
            self.orange_high = (50, 193, 255)        #v250
            self.brown_low = (0, 44, 185)
            self.brown_high = (38, 152, 230)

    def extract_contours(self, image: np.array) -> np.array:
        hsv = self.to_hsv(image)

        if time.time() - self.last_color_update > 1:
            self.update_color_ranges(hsv)
            self.last_color_update = time.time()

        #mask_brown = cv2.inRange(hsv, self.brown_low, self.brown_high)
        mask_white = cv2.inRange(hsv, self.white_low, self.white_high)
        mask_orange = cv2.inRange(hsv, self.orange_low, self.orange_high)

        cnt_white = self.find_contours(mask_white)
        cnt_orange = self.find_contours(mask_orange)
        #cnt_brown = self.find_contours(mask_brown)

        contours_all_masks = [cnt_white, cnt_orange]            #mozna dac brown + white jeszcze

        if Values.SHOW_MASKS:
            cv2.imshow("masks", mask_white + mask_orange)

        if Values.SHOW_ORANGE_MASK:
            cv2.imshow("orange", mask_orange)
        if Values.SHOW_WHITE_MASK:
            cv2.imshow("white", mask_white)

        return contours_all_masks

    def detect(self, frame):

        contours = self.extract_contours(frame)

        detections = []

        for c in range(len(contours)):
            for cnt in contours[c]:

                area = cv2.contourArea(cnt)
                if area > Values.MIN_AREA:

                    bb = cv2.boundingRect(cnt)
                    shape, points, area = self.get_contour_shape(cnt, frame, bb)

                    if shape is not None:

                        mid = [int(bb[0] + 0.5 * bb[2]), int(bb[1] + 0.5 * bb[2])]

                        detection_color = [0, 0, 0]
                        detection_color[c] += 1

                        detection = Detection(bb, detection_color, mid)
                        detections.append(detection)

        return detections

    def get_contour_shape(self, contour, frame, bb):

        shape = None
        area = None
        my_arclength = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * my_arclength, True)
        length = len(approx)
        points = []

        if cv2.isContourConvex(approx):

            if length == 4:
                pass
                """for i in range(length):
                    points.append((approx[i][0][0], approx[i][0][1]))

                distances = [self.my_distance(points[0], points[1]), self.my_distance(points[0], points[2]),
                             self.my_distance(points[0], points[3]), self.my_distance(points[1], points[2]),
                             self.my_distance(points[1], points[3]), self.my_distance(points[2], points[3])]

                distances.sort()

                first_four = distances[:4]

                my_mean = np.mean(first_four)

                differences = np.abs(np.subtract(first_four, my_mean))

                sizes_check = np.greater(differences, 0.1 * my_mean)

                wrong_size = np.any(sizes_check)"""

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
                    r = (bb[2] + bb[3]) / 4
                    area = int(np.pi * r * r)
                    shape = Values.CIRCLE

        return shape, points, area


