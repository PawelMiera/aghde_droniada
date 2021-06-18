import cv2
import queue
import threading
import time


class SavingThread:
    def __init__(self):

        self.queue = queue.Queue()

        self.end_thread = False

        self.thread = threading.Thread(target=self.start_thread)
        self.thread.daemon = True
        self.thread.start()

    def start_thread(self):
        while True:

            if self.end_thread:
                break

            if not self.queue.empty():
                item = self.queue.get()

                cv2.imwrite(item[0], item[1])
            else:
                time.sleep(0.01)

    def close(self):
        self.end_thread = True