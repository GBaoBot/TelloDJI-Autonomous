from DroneTello import *

class TelloTrack(TelloDJI):
    def __init__(self, speed=10):
        super().__init__(speed)

    
    def suggest_action_when_tracking(self, frame, bounding_box): 
        self.send_rc_control = False 
 
        x1, y1, x2, y2 = bounding_box 
        w = x2 - x1 
        h = y2 - y1 
        cx = x1 + w // 2
        cy = y1 + h // 2 
        
        fh, fw, _ = frame.shape
        fcx = fw // 2
        fcy = fh // 2

        error_x = fcx - cx
        error_y = fcy - cy

        if abs(error_x) > fcx * 0.1:  # 10% margin
            self.yaw_velocity = -self.speed if error_x > 0 else self.speed
        else:
            self.yaw_velocity = 0

        if abs(error_y) > fcy * 0.1:  # 10% margin
            self.up_down_velocity = self.speed if error_y > 0 else -self.speed
        else:
            self.up_down_velocity = 0
          
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
            time.sleep(0.1)
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break 
         
        cv2.destroyAllWindows() 
        self.tello.land() 
        self.tello.streamoff() 
        self.tello.end()