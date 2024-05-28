from SafeThread import *
from djitellopy import Tello 

class TelloBase:
    import cv2
    from queue import Queue
    def __init__(self, speed) -> None:
        # Tello Drone
        self.tello = Tello()
        self.maxSpeed = speed


        # Video
        self.frame_size = (640, 480)
        self.readFrame = None
        self.q = self.Queue()

        # Thread
        self.videoThread = SafeThread(self.__video)

 

    def connect(self):
        try:
            self.tello.connect()
            self.tello.set_speed(self.maxSpeed)

        except Exception as e:
            print(f"Error connecting to drone: {e}")
    
    def cameraOn(self):
        try:
            self.tello.stream_on()
            self.readFrame = self.tello.get_frame_read()

        except Exception as e:
            print(f"Error opening camera: {e}")

    def __video(self):
        pass