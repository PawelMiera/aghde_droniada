from camera.camera import Camera
from camera.camera import BasicCamera
import cv2
import os
from datetime import datetime
import time

now = datetime.now()

camera = BasicCamera()
folder = os.path.join("images", str(now.strftime("%H_%M_%S")))
print(folder)
try:
    os.mkdir(folder)
except OSError:
    print("Creation of the directory failed")

j = 0
start = time.time()
while True:

    frame = camera.get_frame()

    if frame is None:
        continue

    cv2.imshow("test", frame)
    t = round((time.time() - start) * 1000)
    file_name = '%d.jpg' % t
    file_name = str(j) + "_" + file_name
    cv2.imwrite(os.path.join(folder, file_name), frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    j+=1