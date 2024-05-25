from djitellopy import Tello 
import cv2 
import numpy as np 
from ultralytics import YOLO 
from pynput import keyboard 
import time
 
 
class TelloDJI(object):  
    def __init__(self, speed=10): 
        self.should_stop = False # To note when to stop
        self.for_back_velocity = 0 
        self.left_right_velocity = 0 
        self.up_down_velocity = 0 
        self.yaw_velocity = 0 
        self.speed = speed # Max Speed
 
        self.send_rc_control = False 
 
        # Init Tello object that interacts with the Tello drone 
        self.tello = Tello() 


    def connect(self):
        try:
            self.tello.connect()
            self.tello.set_speed(self.speed)
        except Exception as e:
            print(f"Error connecting to Tello: {e}")


    def camera_on(self):
        try:
            self.tello.streamoff()
            time.sleep(1)  # Ensure the stream is properly turned off
            self.tello.streamon()
            time.sleep(2)  # Wait for the stream to initialize properly
            self.frame_read = self.tello.get_frame_read()
        except Exception as e:
            print(f"Error turning on camera: {e}")

 

    def get_frame(self): 
        if self.frame_read.stopped: 
            print("Frame read stopped")
            return None
         
        frame = self.frame_read.frame 
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
        return frame 


    def init_model(self): 
        model = YOLO("yolov8n.pt") 
 
        return model 


    def stop_moving(self):
        self.for_back_velocity = 0 
        self.left_right_velocity = 0 
        self.up_down_velocity = 0 
        self.yaw_velocity = 0
        self.send_rc_control = True
 

    def update(self): 
        if self.send_rc_control: 
            self.tello.send_rc_control(
                self.left_right_velocity, 
                self.for_back_velocity, 
                self.up_down_velocity, 
                self.yaw_velocity)
            

    def battery(self): 
        try:
            battery_level = self.tello.get_battery()
            return battery_level
        except Exception as e:
            print(f"Error getting battery level: {e}")
            return None

if __name__ == '__main__': 
    # try_control() 
    drone = TelloDJI()
    drone.connect()
    print(drone.battery())
    # battery_tello()