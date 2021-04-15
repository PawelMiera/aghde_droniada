import cv2
import os
import pandas as pd
import time
import pickle
import numpy as np

dump = []

for i in range(144, 418):
    f = os.path.join('tests', "to train")

    fpath = str(i) + '.jpg'
    fpath = os.path.join(f, fpath)

    img = cv2.imread(fpath)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, (65, 0, 210), (178, 81, 255))
    mask += cv2.inRange(hsv, (161, 26, 128), (203, 73, 225))
    mask += cv2.inRange(hsv, (10, 35, 155), (57, 114, 255))
    mask += cv2.inRange(hsv, (0, 36, 128), (9, 75, 138))

    cnt, h = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if i == 0:
        cv2.imshow("mask", mask)
        cv2.imshow("xd", img)
        cv2.waitKey(0)

    for c in cnt:
        if cv2.contourArea(c) > 1000:
            cv2.drawContours(img, [c], -1, (0, 255, 0), 3)
            cv2.imshow("xd", img)
            cv2.waitKey(1)
            start = time.time()
            c[:, :, 1] = np.subtract(c[:, :, 1], np.min(c[:, :, 1]) - 2)
            c[:, :, 0] = np.subtract(c[:, :, 0], np.min(c[:, :, 0]) - 2)

            M = cv2.moments(c)
            huMoments = cv2.HuMoments(M)

            huMoments = -1 * np.sign(huMoments) * np.log10(np.abs(huMoments))
            huMoments = np.nan_to_num(huMoments)

            a = input(str(i)+". Podaj: ")

            klasa = -1

            if a == "t":
                klasa = 0
            elif a == "c":
                klasa = 1
            elif a == "s":
                klasa = 2

            hull = cv2.convexHull(c)
            hullArea = cv2.contourArea(hull)
            solidity = cv2.contourArea(c) / float(hullArea)

            if klasa != -1:
                hu = huMoments.reshape((1, 7)).tolist()[0] + [cv2.arcLength(c, True)] + [solidity] + [klasa]
                dump.append(hu)

cols = ["hu1", "hu2", "hu3", "hu4", "hu5", "hu6", "hu7", "arcLen", "solidity",  "class"]

df = pd.DataFrame(dump, columns=cols)
df.to_csv("my.csv", index=None)
