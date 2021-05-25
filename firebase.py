from random import random
from firebase.firebase import FirebaseConnection


if __name__ == "__main__":
    firebaseConnection = FirebaseConnection()

    for i in range(3):
        firebaseConnection.publish_detection(51.172383 + 0.08 * i, 17.98839 + 0.12 * i, 2.5, "it is some description12",
                                             "images/" + "firebase/" + str(i) + ".jpg")
        firebaseConnection.publish_telemetry(random(), random(), random())

    firebaseConnection.close()