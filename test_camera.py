from camera.camera import Camera
from camera.camera import BasicCamera
import cv2
from datetime import datetime

import time

now = datetime.now()

camera = BasicCamera()

i = 0

last_time = time.time()
while True:

    frame = camera.get_frame()

    if frame is None:
        continue
    cv2.imshow("test", frame)

    i += 1
    if time.time() - last_time > 1:
        last_time = time.time()
        print(i)
        i=0

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
