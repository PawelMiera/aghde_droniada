from settings.settings import Values
from detector.detector import Detector
from camera.camera import Camera, BasicCamera2
from telemetryThread.telemetry import TelemetryThread
from telemetry.telemetry import Telemetry
from positionCalculator.positionCalculator import PositionCalculator
import cv2
import time
import traceback
import os
import csv
from datetime import datetime


def save_frame_crop(frame, rectangle, filename):
    if rectangle is not None:
        x, y, w, h = rectangle
        x1 = x - 2*w
        y1 = y - 2*h
        x2 = x + 3 * w
        y2 = y + 3 * h

        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(Values.CAMERA_WIDTH, x2)
        y2 = min(Values.CAMERA_HEIGHT, y2)
        crop = frame[y1:y2, x1:x2]
        crop = cv2.resize(crop, (400, 400))
        cv2.imwrite(filename, crop)


def mode_0():
    camera = Camera()
    detector = Detector()
    telemetry = Telemetry()
    position_calculator = PositionCalculator(telemetry)
    all_detections = []
    confirmed_detections = []
    confirmed_detection_id = 0

    detections_file = open(save_directory + "/detections.txt", "w")

    time_index = 0
    id = 150

    base_path = 'D:/mission_images/2021_05_27_09_49_31/'

    with open(base_path + 'telemetry.txt') as f:
        reader = csv.reader(f)
        data = list(reader)

    if Values.PRINT_FPS:
        last_time = time.time()
        ind = 0
    while True:
        try:

            path = base_path + "images/" + str(id) + ".png"

            frame = cv2.imread(path)
            # self.frame = self.camera.get_frame()

            if frame is None:
                continue

            update_detections_file = False

            frame = cv2.resize(frame, (Values.CAMERA_WIDTH, Values.CAMERA_HEIGHT))

            detections = detector.detect(frame)
            telemetry.update_telemetry(data[id])

            position_calculator.update_meters_per_pixel()
            position_calculator.calculate_max_meters_area()
            position_calculator.calculate_extreme_points()  # tylko potrzebne zeby wyswietlic stare wykrycia

            for d in detections:
                lat, lon = position_calculator.calculate_point_lat_long(d.middle_point)
                d.update_lat_lon(lat, lon)
                d.area_m = position_calculator.calculate_area_in_meters_2(d.area)
                d.draw_detection(frame)

                for conf_d in confirmed_detections:
                    if d.check_detection(conf_d):
                        conf_d += d
                        conf_d.last_seen = time_index
                        d.to_delete = True
                        update_detections_file = True
                        break
                if d.to_delete:
                    continue

                for all_d in all_detections:
                    if d.check_detection(all_d):
                        all_d += d
                        all_d.last_seen = time_index
                        d.to_delete = True
                        all_d.rectangle = d.rectangle
                        break
                if not d.to_delete:
                    d.last_seen = time_index
                    all_detections.append(d)

            for all_d in all_detections:
                if all_d.seen_times > 20:
                    all_d.detection_id = confirmed_detection_id
                    confirmed_detection_id += 1
                    filename = save_directory + "/detections/" + str(all_d.detection_id) + ".jpg"
                    save_frame_crop(frame, all_d.rectangle, filename)
                    all_d.filename = filename
                    confirmed_detections.append(all_d)
                    update_detections_file = True
                    all_d.to_delete = True
                elif all_d.seen_times > 8:
                    if time_index - all_d.last_seen > 800:
                        all_d.to_delete = True
                else:
                    if time_index - all_d.last_seen > 20:
                        all_d.to_delete = True

            all_detections = list(filter(lambda x: not x.to_delete, all_detections))

            detections_file_text = "///////////////////////\n"

            for conf_d in confirmed_detections:

                if update_detections_file:
                    detections_file_text += conf_d.getString()

                my_mid = position_calculator.get_detection_on_image_cords(conf_d.latitude, conf_d.longitude)
                if my_mid is not None:
                    conf_d.draw_confirmed_detection(frame, my_mid)

            if update_detections_file:
                detections_file.write(detections_file_text)

            cv2.putText(frame, telemetry.to_string(), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255))
            cv2.imshow("frame", frame)

            time_index += 1
            id += 1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            if Values.PRINT_FPS:
                ind += 1
                if time.time() - last_time > 1:
                    print("FPS:", ind)
                    ind = 0
                    last_time = time.time()

        except Exception:
            print("Some error accrued: ")
            traceback.print_exc()

    camera.close()


def mode_1():
    camera = BasicCamera2()
    telemetry = TelemetryThread()
    position_calculator = PositionCalculator(telemetry)  # do wywalenia
    img_id = 0
    telemetry_file = open(save_directory + "/telemetry.txt", "a+")
    if Values.PRINT_FPS:
        last_time = time.time()
        ind = 0
    while True:
        try:

            frame = camera.get_frame()
            if frame is None:
                continue

            if telemetry.altitude > Values.MIN_ALTITUDE:
                cv2.imwrite(save_directory + "/images/" + str(img_id) + ".png", frame)
                img_id += 1
                telemetry_file.write(telemetry.to_string() + "\n")

            if telemetry.latitude != 0 and telemetry.altitude > 2:
                position_calculator.update_meters_per_pixel()
                position_calculator.calculate_max_meters_area()
                position_calculator.calculate_extreme_points()

            cv2.putText(frame, telemetry.to_string(), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255))
            cv2.imshow("frame", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            if Values.PRINT_FPS:
                ind += 1
                if time.time() - last_time > 1:
                    print("FPS:", ind)
                    ind = 0
                    last_time = time.time()

        except Exception:
            print("Some error accrued: ")
            traceback.print_exc()
    telemetry_file.close()
    camera.close()


def mode_2():
    camera = BasicCamera2()
    detector = Detector()
    telemetry = TelemetryThread()
    position_calculator = PositionCalculator(telemetry)
    all_detections = []
    confirmed_detections = []
    confirmed_detection_id = 0
    time_index = 0

    detections_file = open(save_directory + "/detections.txt", "w")

    if Values.PRINT_FPS:
        last_time = time.time()
        ind = 0

    while True:
        try:

            frame = camera.get_frame()

            if frame is None:
                continue

            update_detections_file = False

            if telemetry.altitude > Values.MIN_ALTITUDE:
                detections = detector.detect(frame)

                position_calculator.update_meters_per_pixel()
                position_calculator.calculate_max_meters_area()
                position_calculator.calculate_extreme_points()  # tylko potrzebne zeby wyswietlic stare wykrycia

                for d in detections:
                    lat, lon = position_calculator.calculate_point_lat_long(d.middle_point)
                    d.update_lat_lon(lat, lon)
                    d.area_m = position_calculator.calculate_area_in_meters_2(d.area)
                    d.draw_detection(frame)

                    for conf_d in confirmed_detections:
                        if d.check_detection(conf_d):
                            conf_d += d
                            conf_d.last_seen = time_index
                            d.to_delete = True
                            update_detections_file = True
                            break
                    if d.to_delete:
                        continue

                    for all_d in all_detections:
                        if d.check_detection(all_d):
                            all_d += d
                            all_d.last_seen = time_index
                            d.to_delete = True
                            all_d.rectangle = d.rectangle
                            break
                    if not d.to_delete:
                        d.last_seen = time_index
                        all_detections.append(d)

                for all_d in all_detections:
                    if all_d.seen_times > 20:
                        all_d.detection_id = confirmed_detection_id
                        confirmed_detection_id += 1
                        filename = save_directory + "/detections/" + str(all_d.detection_id) + ".jpg"
                        save_frame_crop(frame, all_d.rectangle, filename)
                        all_d.filename = filename
                        confirmed_detections.append(all_d)
                        update_detections_file = True
                        all_d.to_delete = True
                    elif all_d.seen_times > 8:
                        if time_index - all_d.last_seen > 800:
                            all_d.to_delete = True
                    else:
                        if time_index - all_d.last_seen > 20:
                            all_d.to_delete = True

                all_detections = list(filter(lambda x: not x.to_delete, all_detections))  # do sprawdzenia

                detections_file_text = "///////////////////////\n"

                for conf_d in confirmed_detections:

                    if update_detections_file:
                        detections_file_text += conf_d.getString()

                    my_mid = position_calculator.get_detection_on_image_cords(conf_d.latitude, conf_d.longitude)
                    if my_mid is not None:
                        conf_d.draw_confirmed_detection(frame, my_mid)

                if update_detections_file:
                    detections_file.write(detections_file_text)

            cv2.putText(frame, telemetry.to_string(), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255))
            cv2.imshow("frame", frame)

            time_index += 1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            if Values.PRINT_FPS:
                ind += 1
                if time.time() - last_time > 1:
                    print("FPS:", ind)
                    ind = 0
                    last_time = time.time()

        except Exception:
            print("Some error accrued: ")
            traceback.print_exc()

    camera.close()
    detections_file.close()


if __name__ == '__main__':

    save_directory = Values.SAVED_IMAGES_DIRECTORY + '/' + datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    try:
        os.makedirs(save_directory + "/images")
        os.makedirs(save_directory + "/detections")
        print("Directory ", save_directory, " Created ")
    except FileExistsError:
        print("Directory ", save_directory, " already exists")

    if Values.MODE == 0:
        mode_0()
    elif Values.MODE == 1:
        mode_1()
    elif Values.MODE == 2:
        mode_2()
