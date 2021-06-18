from threading import Thread
import cv2
import time
import numpy as np


class MainLoop(Thread):


    def get_image_mask(self, hsv):
        v = hsv[:, :, 2]
        #start = time.time()
        #mean = np.mean(v)
        #print(mean, time.time() - start, end="")

        #start = time.time()
        self.median = np.median(v)
        #print(self.median, time.time() - start)

        val = self.median

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
            self.orange_low = (0, 90, 212)      #168
            self.orange_high = (50, 228, 255)
            self.brown_low = (0, 65, 154)           #s92         #sprawdz braz
            self.brown_high = (20, 147, 240)         #v198  v220

        elif 65 <= val < 73:
            self.white_low = (0, 0, 210)
            self.white_high = (190, 40, 255)
            self.orange_low = (0, 130, 224)      #s110  s 105
            self.orange_high = (52, 150, 255)    #s 172
            self.brown_low = (0, 46, 175)
            self.brown_high = (198, 135, 255)     #v235  s91

        else:
            self.white_low = (0, 0, 210)
            self.white_high = (190, 40, 255)
            self.orange_low = (0, 99, 225)
            self.orange_high = (50, 193, 255)        #v250
            self.brown_low = (0, 44, 185)
            self.brown_high = (38, 152, 230)

        mask_white = cv2.inRange(hsv, self.white_low, self.white_high)
        mask_orange = cv2.inRange(hsv, self.orange_low, self.orange_high)
        mask_brown = cv2.inRange(hsv, self.brown_low, self.brown_high)

        cv2.imshow("white", mask_white)
        cv2.imshow("brown", mask_brown)
        cv2.imshow("orange", mask_orange)
        cv2.waitKey(1)


        """cts, h = cv2.findContours(mask_white + mask_orange + mask_brown, cv2.RETR_LIST,
                                  cv2.CHAIN_APPROX_SIMPLE)

        for c in cts:
            area = cv2.contourArea(c)
            cv2.drawContours(hsv, c, -1, (0, 0, 0), 3)
            cv2.imshow("mhsv", hsv)
            print(area)
            cv2.waitKey(0)"""


    def __init__(self):
        Thread.__init__(self)
        self.stop_loop = False
        self.frame = None

        self.output_mask = None

        self.h = 0
        self.s = 0
        self.v = 0

        self.window = None

        self.min_hsv = (0, 0, 0)
        self.max_hsv = (255, 255, 255)

        self.min_masks = []
        self.max_masks = []

        self.masks = []

        self.id = 0

        self.show_current = True

        self.PRINT_FPS = False

        self.median = 0

    def mouseRGB(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:  # checks mouse left button down condition
            bgr = [self.frame[y, x, 0], self.frame[y, x, 1], self.frame[y, x, 2]]

            hsv = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0]

            self.h = hsv[0]
            self.s = hsv[1]
            self.v = hsv[2]

            self.min_hsv = np.maximum((self.h - 30, self.s - 30, self.v - 30), (0, 0, 0))
            self.max_hsv = np.minimum((self.h + 30, self.s + 30, self.v + 30), (255, 255, 255))

            if self.window is not None:
                self.window.sliders[0].setValue(self.min_hsv[0])
                self.window.sliders[1].setValue(self.min_hsv[1])
                self.window.sliders[2].setValue(self.min_hsv[2])
                self.window.sliders[3].setValue(self.max_hsv[0])
                self.window.sliders[4].setValue(self.max_hsv[1])
                self.window.sliders[5].setValue(self.max_hsv[2])

    def run(self):

        if self.PRINT_FPS:
            last_time = time.time()
            ind = 0

        cv2.namedWindow('bgr')
        cv2.setMouseCallback('bgr', self.mouseRGB)

        last_id = -1

        self.id = 0

        while True:
            if self.stop_loop:
                break

            path = "tests/to_train2/" + str(self.id) + ".png"

            path = 'D:/mission_images/12/images'

            self.frame = cv2.imread(path + "/" + str(self.id) + ".png")

            if self.frame is None:
                continue
            def_frame = self.frame
            h, w = self.frame.shape[:-1]
            h = int(h / 2)
            w = int(w / 2)

            self.frame = cv2.resize(self.frame, (w, h))
            hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
            #cv2.imshow("hsv", hsv)

            self.get_image_mask(hsv)

            """if self.id != last_id:
                def_hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
                v = def_hsv[:, :, 2]
                median = np.median(v)

                print(self.id, median)
                cv2.imshow("hsv", hsv)
                last_id = self.id"""

            if self.show_current:
                mask_base = cv2.inRange(hsv, self.min_hsv, self.max_hsv)
            else:
                mask_base = np.zeros((h, w))

            for mask in self.masks:
                mask_base += cv2.inRange(hsv, mask[0], mask[1])

            self.output_mask = mask_base.copy()

            cv2.imshow("bgr", self.frame)
            cv2.imshow("mask", mask_base)

            cv2.waitKey(1)

            if self.PRINT_FPS:
                ind += 1
                if time.time() - last_time > 1:
                    print("FPS:", ind)
                    ind = 0
                    last_time = time.time()

    def save_mask(self):
        if self.output_mask is not None:
            cv2.imwrite("mask.png", self.output_mask)

    def close(self):
        self.stop_loop = True
