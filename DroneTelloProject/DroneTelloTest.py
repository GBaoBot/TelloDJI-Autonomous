from djitellopy import Tello 
import cv2 
# import pygame 
import numpy as np 
# import time 
from ultralytics import YOLO 
 
 
# Speed of the drone 
S = 20 
# Frames per second of the pygame window display 
# A low number also results in input lag, as input information is processed once per frame. 
FPS = 120 
 
 
class TelloDJI(object): 
    """ Maintains the Tello display and moves it through the keyboard keys. 
        Press escape key to quit. 
        The controls are: 
            - T: Takeoff 
            - L: Land 
            - Arrow keys: Forward, backward, left and right. 
            - A and D: Counter clockwise and clockwise rotations (yaw) 
            - W and S: Up and down. 
    """ 
 
    def __init__(self): 
        # Init pygame 
        # pygame.init() 
 
        # Creat pygame window 
        # pygame.display.set_caption("Tello video stream") 
        # self.screen = pygame.display.set_mode([480, 480]) 
        # self.screen.fill([0, 0, 0]) 
 
        # Drone velocities between -100~100 
        self.should_stop = False 
        self.for_back_velocity = 0 
        self.left_right_velocity = 0 
        self.up_down_velocity = 0 
        self.yaw_velocity = 0 
        self.speed = 10 
 
        self.send_rc_control = False 
 
        # Init Tello object that interacts with the Tello drone 
        self.tello = Tello() 
        self.tello.connect() 
        self.tello.set_speed(self.speed) 
 
        # Camera 
        self.tello.streamoff() 
        self.tello.streamon() 
        self.frame_read = self.tello.get_frame_read() 
 
        # create update timer 
        # pygame.time.set_timer(pygame.USEREVENT + 1, 1000 // FPS) 
 
    def get_frame(self): 
        if self.frame_read.stopped: 
            return 
         
        frame = self.frame_read.frame 
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
        # frame = np.rot90(frame) 
        # frame = np.flipud(frame) 
        return frame 
 
    def init_model(self): 
        model = YOLO("yolov8n.pt") 
 
        return model 
     
    def set_stationary(self): 
        self.for_back_velocity = 0 
        self.left_right_velocity = 0 
        self.up_down_velocity = 0 
        self.yaw_velocity = 0 
 
    def suggest_action_when_tracking(self, frame, bounding_box): 
        action = 0 
        # forward = 1 
        # backward = 2 
        # left = 3 
        # right = 4 
        # up = 5 
        # down = 6 
        # self.for_back_velocity = 0 
        self.send_rc_control = False 
 
        x1, y1, x2, y2 = bounding_box 
        cx = (x1 + x2) / 2 
        cy = (y1 + y2) / 2 
        w = x2 - x1 
        h = y2 - y1 
 
        fh, fw, _ = frame.shape 
        deadzonex = fw / 4 
        deadzoney = fh / 4 
 
        if (cx < (fw / 2 - deadzonex)): 
            action = 3 
            self.yaw_velocity = -S 
            print('Turn Left') 
        elif (cx > (fw / 2 + deadzonex)): 
            action = 4 
            self.yaw_velocity = S 
            print('Turn Right') 
        # elif (w*h < fh*fw / 15): 
        #     action = 1 
        #     self.for_back_velocity = S 
        #     print('Move Forward') 
        # elif (w*h > fh*fw / 15): 
        #     action = 2 
        #     self.for_back_velocity = -S 
        #     print('Move Backward') 
        elif (cy < (fh / 2 - deadzoney)): 
            action = 5 
            self.up_down_velocity = S 
            print('Fly UP') 
        elif (cy > (fh / 2 + deadzoney)): 
            action = 6 
            self.up_down_velocity = -S 
            print('Fly Down') 
        else: 
            self.yaw_velocity = 0 
            self.for_back_velocity = 0 
            self.up_down_velocity = 0 
            return 
        # self.for_back_velocity = 0 
         
        self.send_rc_control = True 
        return 
    def track_human(self): 
        # self.tello.takeoff() 
        model = self.init_model() 
        cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE) 
        cv2.resizeWindow('frame', 480, 480) 
        while True: 
            frame = self.get_frame()
            result = model.track(frame, classes=[0], persist=True) 
            cv2.imshow('frame', frame) 
            
            if len(result[0].boxes.xyxy) != 0: 
                box = result[0].boxes.xyxy[0] 
                self.suggest_action_when_tracking(frame, box) 
            else: 
                # Ensure the drone stays stationary if no object is detected 
                self.set_stationary() 
 
            self.update()  # Ensure update is called regularly to send control commands 
 
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break 
         
        cv2.destroyAllWindows() 
        self.tello.land() 
        self.tello.streamoff() 
        self.tello.end() 
 
 
    def update(self): 
        """ Update routine. Send velocities to Tello. 
        """ 
        if self.send_rc_control: 
            self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity, 
                self.up_down_velocity, self.yaw_velocity) 
 
    def battery(self): 
        return self.tello.get_battery() 
     
def try_track_human(): 
    drone = TelloDJI() 
 
    drone.track_human() 
     
def battery_tello(): 
    drone = TelloDJI() 
     
    print(drone.battery()) 
 
if __name__ == '__main__': 
    # try_control() 
    try_track_human() 
    # battery_tello()