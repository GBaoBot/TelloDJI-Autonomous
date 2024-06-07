from djitellopy import Tello 
from queue import Queue
import cv2 
from utils.SafeThread import *
from utils.BrainControl import *
from utils.BrainTrack import *
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
        self.clickCoor = (0, 0)
        
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


    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.clickCoor = (x, y)
            print(f"Clicked at: {self.clickCoor}")


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
            self.controlEvent.wait(0.01)
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
        # cv2.namedWindow('frame')
        
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
        cv2.setMouseCallback("frame", self.mouse_callback)
        videow = cv2.VideoWriter('out.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 60, (self.frame_size))
        writevideo = False
        # Track
        self.brainTrack = BrainTrack(self)
        self.brainTrack.set_tracking()
        self.brainTrack.onTracking()
        
        # Control
        self.brainControl = BrainControl(self, self.speed)
        self.brainControl.startReadFromKeyboard()
       
        try:
            while True:
                try: 
                    frame = self.get_frame()
                    if frame is None: continue
                    
                    self.brainTrack.process_frame(frame)
                    if self.clickCoor != (0, 0):
                        self.brainTrack.process_clickCoor(self.clickCoor)
                        self.clickCoor = (0, 0)
                    self.brainTrack.draw_detections(frame)
                    
                    cv2.imshow('frame', frame)
                    
                    k = cv2.waitKey(self.pSpeedVideo) & 0xFF
                    if k == 27:
                        break
                    if k == ord('v'):
                        if writevideo == False : writevideo = True
                        else: writevideo = False
                    
                    if writevideo == True:
                        videow.write(frame)
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
    tello = TelloMain(10)
    
    print("Please choose option:")
    print("- Option 0: Show battery")
    print("- Option 1: Control")
    print("- Option 2: Track Human who raises hand")
    
    print("Please type the option number (Eg: 1 or 2...)")
    option = input("Choose your option: ")
    
    if option == '0':
        tello.connect()
        print(f"Battery: {tello.get_battery()}")
    elif option == '1':
        print("You chose to CONTROL!")
        tello.modeControl()
    elif option == '2':
        print("You chose to TRACK!")
        tello.modeTrack()
    else:
        print("Invalid!")
    # k = input()
        
