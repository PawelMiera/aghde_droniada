import cv2
import queue
import threading
import time
import traceback


class SavingThread:
    def __init__(self, firebaseConnection):

        self.firebaseConnection = firebaseConnection
        self.queue = queue.Queue()

        self.end_thread = False

        self.thread = threading.Thread(target=self.start_thread)
        self.thread.daemon = True
        self.thread.start()

    def start_thread(self):
        while True:
            try:
                if self.end_thread:
                    break

                if not self.queue.empty():
                    item = self.queue.get()

                    if item[0] == 0:
                        d = item[1]
                        self.firebaseConnection.publish_detection(d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7])

                    elif item[0] == 1:
                        d = item[1]
                        self.firebaseConnection.update_all_detections(d)

                    elif item[0] == 2:
                        d = item[1]
                        self.firebaseConnection.publish_telemetry(d[0], d[1], d[2])

                    elif item[0] == 3:
                        cv2.imwrite(item[1], item[2])

                else:
                    time.sleep(0.01)
            except Exception:
                print("Some error accrued: ")
                traceback.print_exc()


    def close(self):
        self.end_thread = True