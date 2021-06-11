import pyrebase
import os


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

    def stream_handler(self, message):
        print(message)

    def publish_detection(self, lat, long, area, description, path, seen_times):
        filename = os.path.basename(path)
        firebase_path = self.storage_cloud_path + filename
        self.publish_image(path, firebase_path)
        result = self.database.child("drones").child(self.drone_nr).child("detections").get()

        try:
            number_id = str(len(result.val()))
        except:
            number_id = "0"

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
        pass

    def publish_image(self, path, firebase_path):
        self.storage.child(firebase_path).put(path)

    def publish_telemetry(self, lat, lon, alt):
        data = {
            'altitude': alt,
            'latitude': lat,
            'longitude': lon
        }
        self.database.child("drones").child(self.drone_nr).child("telemetry").set(data)

    def close(self):
        self.stream.close()
