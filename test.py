from telemetry.telemetry import Telemetry
from positionCalculator.positionCalculator import PositionCalculator
import cv2
from settings.settings import Values
from detector.detector import Detector
import time

if __name__ == '__main__':
    frame = cv2.imread("images/pole.png")
    telemetry = Telemetry()
    positionCalculator = PositionCalculator()
    detector = Detector()

    width, height = frame.shape[1::-1]

    altitude = 10
    x_offset = 0
    y_offset = 0
    azimuth = 0
    telemetry.update_telemetry_manually(width / 2, height / 2, azimuth, altitude)



    try:
        if Values.PRINT_FPS:
            last_time = time.time()
            ind = 0
        while True:
            frame = cv2.imread("images/pole.png")
            left = x_offset + int(width/2 - width * altitude / 30)
            right = x_offset + int(width/2 + width * altitude / 30)
            top = y_offset + int(height/2 - height * altitude / 30)
            bot = y_offset + int(height/2 + height * altitude / 30)

            if bot > height:
                y_offset -= 5
                bot = height
            if top < 0:
                y_offset += 5
                top = 0
            if right > width:
                x_offset -= 5
                right = width
            if left < 0:
                x_offset += 5
                left = 0

            prepared_frame = frame[top:bot, left:right]
            print(left, right, top, bot, altitude)
            detections = detector.detect(prepared_frame)

            for d in detections:
                d.draw_detection(prepared_frame)

            cv2.imshow("frame", prepared_frame)
            key = cv2.waitKey(0)
            print(key)

            if key == 97:
                x_offset -= 5
            elif key == 100:
                x_offset += 5
            elif key == 119:
                y_offset -= 5
            elif key == 115:
                y_offset += 5
            elif key == 120:
                altitude += 1
            elif key == 122:
                altitude -= 1
            elif key == 113:
                azimuth += 5
            elif key == 101:
                azimuth -= 5

            if azimuth > 360:
                azimuth -= 360
            elif azimuth < 0:
                azimuth += 360

            if altitude > 28:
                altitude = 28
            elif altitude < 3:
                altitude = 3

            if key == 27:
                break

            if Values.PRINT_FPS:
                ind += 1
                if time.time() - last_time > 1:
                    print("FPS:", ind)
                    ind = 0
                    last_time = time.time()

    except ValueError as er:
        print("Some error accured: ", str(er))
    except KeyboardInterrupt:
        print("Closing")
