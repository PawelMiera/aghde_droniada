from threading import Thread
import cv2
import time
import numpy as np


class MainLoop(Thread):

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

        self.id = 820

        self.show_current = True

        self.PRINT_FPS = False

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

        while True:
            if self.stop_loop:
                break

            path = "tests/to_train2/" + str(self.id) + ".png"
            self.frame = cv2.imread(path)

            if self.frame is None:
                continue

            h, w = self.frame.shape[:-1]
            h = int(h / 2)
            w = int(w / 2)

            self.frame = cv2.resize(self.frame, (w, h))
            hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
            cv2.imshow("hsv", hsv)

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
