from time import sleep

import cv2


class PiCamera:
    def __init__(self, resolution):
        self.resolution = resolution
        self.framerate = 30
        self.cap = cv2.VideoCapture('Videos/test.avi')

    def capture_continuous(self, output, format, use_video_port):
        cap = self.cap
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                sleep(0.05)
                yield cv2.cvtColor(cv2.resize(frame, self.resolution), cv2.COLOR_BGR2GRAY)
            else:
                break

    def capture(self, view, format):
        cap = self.cap
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                sleep(0.05)
                view.array = cv2.resize(frame, self.resolution)
                return view
        return None

    def close(self):
        pass
