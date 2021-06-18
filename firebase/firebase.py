import pyrebase
import os
import threading, queue
import time
import os.path
import traceback


class FirebaseConnection:
    def __init__(self):
        config = {
            "apiKey": "AIzaSyAglFX49k28WWJqS33SQEpct3kE_d3JDZs",
            "authDomain": "droniada-f604a.firebaseapp.com",
            "databaseURL": "https://droniada-f604a-default-rtdb.firebaseio.com",
            "projectId": "droniada-f604a",
            "storageBucket": "droniada-f604a.appspot.com",
            "messagingSenderId": "65160484994",
            "appId": "1:65160484994:web:f38e43420da263ba44bc9b"
        }

        self.firebase = pyrebase.initialize_app(config)

        self.storage = self.firebase.storage()

        self.database = self.firebase.database()

        result = self.database.child("drones").get()

        try:
            drone_nr = len(result.val())
            self.drone_nr = str(drone_nr)
        except:
            self.drone_nr = "0"

        self.storage_cloud_path = "images/" + self.drone_nr + "/"

        self.stream = self.database.child("drones").child(self.drone_nr).child("go_to").stream(self.stream_handler)
        self.publish_telemetry(0, 0, 0)

        #self.queue = queue.Queue()

        self.end_thread = False

        #self.thread = threading.Thread(target=self.start_thread)
        #self.thread.daemon = True
        #self.thread.start()

    def start_thread(self):
        while True:
            try:
                if self.end_thread:
                    break

                if not self.queue.empty():
                    item = self.queue.get()

                    if item[0] == 0:
                        d = item[1]

                        if os.path.isfile(d[5]):
                            self.publish_detection(d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7])
                        else:
                            self.queue.put(item)
                    elif item[0] == 1:
                        d = item[1]
                        self.update_all_detections(d)
                    elif item[0] == 2:
                        d = item[1]
                        self.publish_telemetry(d[0], d[1], d[2])
                else:
                    time.sleep(0.01)
            except Exception:
                print("Some error accrued: ")
                traceback.print_exc()

    def stream_handler(self, message):
        print(message)

    def publish_detection(self, number_id, lat, long, area, description, path, firebase_path, seen_times):

        self.publish_image(path, firebase_path)

        data = {
            'area': area,
            'description': description,
            'latitude': lat,
            'longitude': long,
            'photo': firebase_path,
            'seen_times': seen_times
        }
        self.database.child("drones").child(self.drone_nr).child("detections").child(number_id).set(data)

    def update_all_detections(self, confirmed_detections):
        self.database.child("drones").child(self.drone_nr).child("detections").update(confirmed_detections)

    def publish_image(self, path, firebase_path):
        self.storage.child(firebase_path).put(path)

    def publish_telemetry(self, lat, lon, alt):
        data = {
            'altitude': alt,
            'latitude': lat,
            'longitude': lon
        }
        self.database.child("drones").child(self.drone_nr).child("telemetry").set(data)

    def test(self, mdata):
        self.database.child('test').set(mdata)

    def close(self):
        self.end_thread = True
        self.stream.close()




