from settings.settings import Values
from firebase.firebase import FirebaseConnection
from detector.detector import Detector
from camera.camera import *
from telemetryThread.telemetry import TelemetryThread
from telemetry.telemetry import Telemetry
from positionCalculator.positionCalculator import PositionCalculator
import cv2
import time
import traceback
import os
import csv
from datetime import datetime
from additionalFunctions.additionsalFunctions import get_frame_crop
from savingThread.savingThread import SavingThread


def mode_0():
    camera = Camera()
    detector = Detector()
    telemetry = Telemetry()
    position_calculator = PositionCalculator(telemetry)

    savingThread = SavingThread()

    firebaseConnection = FirebaseConnection()
    last_firebase_update = time.time()

    all_detections = []
    confirmed_detections = []
    confirmed_detection_id = 0

    detections_file = open(save_directory + "/detections.txt", "w")

    time_index = 0
    id = 444

    base_path = 'D:/mission_images/8/'

    with open(base_path + 'output.txt') as f:
        reader = csv.reader(f)
        data = list(reader)

    if Values.PRINT_FPS:
        last_time = time.time()
        ind = 0

    last_telemetry_publish_time = 0

    while True:
        try:

            path = base_path + "images/" + str(id) + ".png"

            frame = cv2.imread(path)
            # self.frame = self.camera.get_frame()

            if frame is None:
                continue

            frame_copy = frame.copy()

            update_detections_file = False

            detections = detector.detect(frame)
            telemetry.update_telemetry(data[id])

            if time.time() - last_telemetry_publish_time > Values.TELEMETRY_UPDATE_TIME:
                last_telemetry_publish_time = time.time()
                firebaseConnection.queue.put((2, (telemetry.latitude, telemetry.longitude, telemetry.altitude)))

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
                        conf_d.update_firebase_detection = True
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
                    savingThread.queue.put((filename, get_frame_crop(frame_copy, all_d.rectangle)))
                    all_d.filename = filename
                    all_d.firebase_path = firebaseConnection.storage_cloud_path + str(all_d.detection_id) + ".jpg"
                    confirmed_detections.append(all_d)
                    firebaseConnection.queue.put((0, (all_d.detection_id, all_d.latitude, all_d.longitude, all_d.area_m,
                                                      all_d.get_description(), all_d.filename, all_d.firebase_path,
                                                      all_d.seen_times)))

                    update_detections_file = True
                    all_d.to_delete = True
                elif all_d.seen_times > 8:
                    if time_index - all_d.last_seen > 800:
                        all_d.to_delete = True
                else:
                    if time_index - all_d.last_seen > 20:
                        all_d.to_delete = True

            all_detections = list(filter(lambda x: not x.to_delete, all_detections))

            detections_file_text = "\n///////////////////////\n"

            if time.time() - last_firebase_update > 1:
                detection_dict = dict()
                update_firebase = False
                for conf_d in confirmed_detections:

                    if conf_d.update_firebase_detection:
                        conf_d.update_firebase_detection = False
                        update_firebase = True
                        det_info = {
                            str(conf_d.detection_id) + '/area': conf_d.area_m,
                            str(conf_d.detection_id) + '/description': conf_d.get_description(),
                            str(conf_d.detection_id) + '/latitude': conf_d.latitude,
                            str(conf_d.detection_id) + '/longitude': conf_d.longitude,
                            str(conf_d.detection_id) + '/seen_times': conf_d.seen_times,
                        }
                        detection_dict.update(det_info)

                if update_firebase:
                    last_firebase_update = time.time()
                    firebaseConnection.queue.put((1, detection_dict))

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
            if cv2.waitKey(0) & 0xFF == ord('q'):
                break

            if Values.PRINT_FPS:
                ind += 1
                if time.time() - last_time > 1:
                    print("FPS:", ind, "Frame count:", savingThread.queue.qsize())
                    ind = 0
                    last_time = time.time()

        except Exception:
            print("Some error accrued: ")
            traceback.print_exc()

    camera.close()
    savingThread.close()
    firebaseConnection.close()


def mode_1():
    camera = BasicCamera2()
    telemetry = TelemetryThread()
    savingThread = SavingThread()

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

                savingThread.queue.put((save_directory + "/images/" + str(img_id) + ".jpg", frame))
                #cv2.imwrite(save_directory + "/images/" + str(img_id) + ".png", frame)
                img_id += 1
                telemetry_file.write(telemetry.to_string() + "\n")

            cv2.putText(frame, telemetry.to_string(), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255))
            cv2.imshow("frame", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            if Values.PRINT_FPS:
                ind += 1
                if time.time() - last_time > 1:
                    print("FPS:", ind, "Frame count:", savingThread.queue.qsize())
                    ind = 0
                    last_time = time.time()

        except Exception:
            print("Some error accrued: ")
            traceback.print_exc()
    telemetry_file.close()
    savingThread.close()
    camera.close()


def mode_2():
    camera = BasicCamera2()
    detector = Detector()
    telemetry = TelemetryThread()
    position_calculator = PositionCalculator(telemetry)
    savingThread = SavingThread()

    firebaseConnection = FirebaseConnection()
    last_firebase_update = time.time()
    last_telemetry_publish_time = 0

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

            frame_copy = frame.copy()

            update_detections_file = False

            if telemetry.altitude > Values.MIN_ALTITUDE:    # and telemetry.state == Values.EXECUTING:

                detections = detector.detect(frame)

                if time.time() - last_telemetry_publish_time > Values.TELEMETRY_UPDATE_TIME:
                    last_telemetry_publish_time = time.time()
                    firebaseConnection.queue.put((2, (telemetry.latitude, telemetry.longitude, telemetry.altitude)))

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
                            conf_d.update_firebase_detection = True
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

                        savingThread.queue.put((filename, get_frame_crop(frame_copy, all_d.rectangle)))

                        all_d.filename = filename
                        all_d.firebase_path = firebaseConnection.storage_cloud_path + str(all_d.detection_id) + ".jpg"
                        confirmed_detections.append(all_d)

                        firebaseConnection.queue.put((0, (all_d.detection_id, all_d.latitude, all_d.longitude,
                                                          all_d.area_m, all_d.get_description(), all_d.filename,
                                                          all_d.firebase_path, all_d.seen_times)))

                        update_detections_file = True
                        all_d.to_delete = True
                    elif all_d.seen_times > 8:
                        if time_index - all_d.last_seen > 800:
                            all_d.to_delete = True
                    else:
                        if time_index - all_d.last_seen > 20:
                            all_d.to_delete = True

                all_detections = list(filter(lambda x: not x.to_delete, all_detections))  # do sprawdzenia

                detections_file_text = "\n///////////////////////\n"

                if time.time() - last_firebase_update > 1:
                    detection_dict = dict()
                    update_firebase = False
                    for conf_d in confirmed_detections:

                        if conf_d.update_firebase_detection:
                            conf_d.update_firebase_detection = False
                            update_firebase = True
                            det_info = {
                                str(conf_d.detection_id) + '/area': conf_d.area_m,
                                str(conf_d.detection_id) + '/description': conf_d.get_description(),
                                str(conf_d.detection_id) + '/latitude': conf_d.latitude,
                                str(conf_d.detection_id) + '/longitude': conf_d.longitude,
                                str(conf_d.detection_id) + '/seen_times': conf_d.seen_times,
                            }
                            detection_dict.update(det_info)

                    if update_firebase:
                        last_firebase_update = time.time()
                        firebaseConnection.queue.put((1, detection_dict))

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
                    print("FPS:", ind, "Frame count:", savingThread.queue.qsize())
                    ind = 0
                    last_time = time.time()

        except Exception:
            print("Some error accrued: ")
            traceback.print_exc()

    camera.close()
    detections_file.close()
    savingThread.close()
    firebaseConnection.close()
    telemetry.close()


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
