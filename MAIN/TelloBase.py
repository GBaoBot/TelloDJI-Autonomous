from SafeThread import *
from djitellopy import Tello 
import cv2
from queue import Queue

class TelloBase:
    
    def __init__(self, speed=30) -> None:
        # Tello Drone
        self.tello = Tello()
        self.maxSpeed = speed
        
        self.left_right = 0
        self.for_back = 0
        self.yaw = 0
        self.up_down = 0
        
        # self.eventlist = []


        # Video
        self.frameSize = (640, 480) # (width, height)
        self.readFrame = None
        self.q = Queue(maxsize=1)
        

        # Thread
        self.videoThread = SafeThread(target=self.__video)
        # self.sendCommandThread = SafeThread(target=self.__sendCommand)


    def connect(self):
        try:
            self.tello.connect()
            self.tello.set_speed(self.maxSpeed)

        except Exception as e:
            print(f"Error connecting to drone: {e}")
    
    
    def cameraOn(self):
        try:
            self.tello.streamon()
            self.readFrame = self.tello.get_frame_read()
            if self.videoThread.is_alive() is not True:  
                
                self.videoThread.start()

        except Exception as e:
            print(f"Error opening camera: {e}")


    def cameraOff(self):
        """Stop video stream
        """
        self.tello.streamoff()
        self.videoThread.stop()
        # self.videoThread.join()
        
        
    def __video(self):
        # self.cameraOn()
        
        while True:
            try:
                frame = self.readFrame.frame
                if frame is not None:
                    frame = cv2.resize(frame, self.frameSize)
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    self.q.put(frame)
                
            except Exception as e:
                print(f"Error reading frame: {e}")
            
            
    def getFrame(self):
        return self.q.get()
    
    
    def setFrameSize(self, height, width):
        self.frameSize = (width, height)
        
    
    # def sendCommand(self):
        
        
        
    def update(self, left_right_velocity, for_back_velocity, up_down_velocity, yaw_velocity): 
        self.tello.send_rc_control(
            left_right_velocity, 
            for_back_velocity, 
            up_down_velocity, 
            yaw_velocity)
        
        
    def getBattery(self):
        return self.tello.get_battery()
        
if __name__ == '__main__':
    tello = TelloBase()
    
    tello.connect()
    # tello.cameraOn()
    
    # while True:
    #     try:
    #         frame = tello.getFrame()
            
    #         if frame is None: continue
            
    #         cv2.imshow("frame", frame)
            
    #         k = cv2.waitKey(1) & 0xFF
            
    #     except Exception as e:
    #         print(f"Error streaming: {e}")            
    #         tello.cameraOff()
    #         break
        
    #     if k == ord('q'):
    #         tello.cameraOff()
    #         break
    
    # cv2.destroyAllWindows()
    
    print(tello.getBattery())