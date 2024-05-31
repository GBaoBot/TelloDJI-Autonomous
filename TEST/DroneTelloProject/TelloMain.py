from djitellopy import Tello 
import cv2 
from SafeThread import *
from queue import Queue
# import time
from pynput import keyboard
from BrainControl import *
from BrainTrack import *
# This would be the main object of tello, all the process will be conducted in another file
 
class TelloMain(object):  
    def __init__(self, speed=10): 
        
        self.tello = Tello() 
        
        # Video
        self.q = Queue()
        self.q.maxsize = 1
        self.frame_size = (640, 480)
        self.videoEvent = threading.Event()
        self.pSpeedVideo = 1
        
        # Control
        self.shouldStop = True
        self.speed = speed # Max Speed
        self.for_back_velocity = 0 
        self.left_right_velocity = 0 
        self.up_down_velocity = 0 
        self.yaw_velocity = 0 
        self.controlEvent = threading.Event()
        self.esc_pressed = False
        self.last_key_pressed = None
        
        # Method
        self.brainControl = None
        self.brainTrack = None
        
        # Thread
        self.videoThread = SafeThread(target=self.__video)
        self.controlThread = SafeThread(target=self.__update)
        
        
    def connect(self):
        try:
            self.tello.connect()
            self.tello.set_speed(self.speed)
        except Exception as e:
            print(f"Error connecting to Tello: {e}")


    def camera_on(self):
        try:
            self.tello.streamon()
            self.frame_read = self.tello.get_frame_read()
            # self.videoEvent.wait(1)  # Wait for the stream to initialize properly
            
            if self.videoThread.is_alive() is not True:  self.videoThread.start()
        except Exception as e:
            # if self.videoThread.is_alive(): self.videoThread.stop()
            print(f"Error turning on camera: {e}")


    def camera_off(self):
        self.tello.streamoff()
        self.videoThread.stop()


    def __video(self):
        while True:
            try: 
                frame = self.frame_read.frame
                
                if frame is not None:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, self.frame_size)
                    
                    self.q.put(frame)
                
            except Exception as e:
                pass


    def get_frame(self): 
        return self.q.get()
    
    def resize_frame(self, height, width):
        self.frame_size = (width, height)


    def updateVelocity(self, left_right_velocity=0, for_back_velocity=0, up_down_velocity=0, yaw_velocity=0): 
        self.for_back_velocity = for_back_velocity
        self.left_right_velocity = left_right_velocity 
        self.up_down_velocity = up_down_velocity 
        self.yaw_velocity = yaw_velocity 
    
    
    def __update(self):
        while True:
            self.controlEvent.wait(0.1)
            self.tello.send_rc_control(
                self.left_right_velocity, 
                self.for_back_velocity, 
                self.up_down_velocity, 
                self.yaw_velocity)
            
            
    def start_communication(self):
        if not self.controlThread.is_alive(): self.controlThread.start()
    
            
    def stop_communication(self):
        self.tello.end()
        self.controlEvent.wait(0.1)
        self.controlThread.stop()


    def battery(self): 
        try:
            battery_level = self.tello.get_battery()
            return battery_level
        except Exception as e:
            print(f"Error getting battery level: {e}")
            return None


    def modeControl(self):
        self.connect()
        self.camera_on()
        self.start_communication()
        cv2.namedWindow('frame')
        
        self.brainControl = BrainControl(self, self.speed)
        self.brainControl.startReadFromKeyboard()
        
        try:
            while True:
                try: 
                    frame = self.get_frame()
                    
                    if frame is None: continue
                    cv2.imshow('frame', frame)
                    if cv2.waitKey(self.pSpeedVideo) & 0xFF == 27:
                        break
                
                except Exception as e:
                    print(f'Error in mode_control: {e}')
                    break
        finally:
            self.brainControl.stopReadFromKeyboard()
            self.camera_off()
            self.stop_communication()
            cv2.destroyAllWindows() 

    def modeTrack(self):
        self.connect()
        self.camera_on()
        self.start_communication()
        cv2.namedWindow('frame')
        
        self.brainTrack = BrainTrack(self)
        self.brainTrack.set_tracking()
        self.brainControl = BrainControl(self, self.speed)
        self.brainControl.startReadFromKeyboard()
       
        try:
            while True:
                try: 
                    frame = self.get_frame()
                    
                    if frame is None: continue
                    
                    self.brainTrack.process_frame(frame)
                    self.brainTrack.draw_detections(frame)
                    
                    cv2.imshow('frame', frame)
                    
                    if cv2.waitKey(self.pSpeedVideo) & 0xFF == 27:
                        break
                
                except Exception as e:
                    print(f'Error in mode_control: {e}')
                    break
        finally:
            self.brainControl.stopReadFromKeyboard()
            self.camera_off()
            self.stop_communication()
            cv2.destroyAllWindows()
            
    def get_battery(self):
        return self.tello.get_battery()
        
if __name__ == "__main__":
    tello = TelloMain(30)
    tello.modeTrack()
    
    # tello.connect()
    # print(tello.get_battery())
        
