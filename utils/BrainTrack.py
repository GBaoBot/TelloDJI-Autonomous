from utils.SafeThread import *
from utils.BrainDetect import *
from utils.Kalman import *
from utils.PID import *
# from TelloMain import *
class BrainTrack(BrainDetect):
    def __init__(self, tello, CONFIDENCE=0.3) -> None:
        super().__init__(CONFIDENCE)
        
        self.tello = tello
        self.tracking = False
        
        # ticker for timebase
        self.ticker = threading.Event()
        
        # PID
        self.normalisation_scale = 100
        self.h = 480
        self.w = 640
        self.pid_x = PID(0.5, r'utils/config/pid_params.yaml')
        self.pid_y = PID(0.5, r'utils/config/pid_params.yaml')
        self.pid_z = PID(0.5, r'utils/config/pid_params.yaml')
        
        # pid_depth = PID(self.normalisation_scale, r'utils/config/pid_params.yaml')
        
        #init 
        self.track = False
        self.frame = None
        self.det = None
        self.tp = None
        self.cx = 0.5
        self.cy = 0.5
        self.cz = 0.2
        
        # tracking options
        self.use_vertical_tracking = True
        self.use_rotation_tracking = True
        self.use_horizontal_tracking = False
        self.use_distance_tracking = True
        
        # processing frequency (to spare CPU time)
        self.cycle_counter = 1
        self.cycle_activation = 10
        
        # Kalman estimator scale factors
        self.kvscale = 6
        self.khscale = 4
        self.distscale = 5
        
        # Set up model
        # self.setUpYOLOv8(MODEL)
        
        # Run thread Tracking
        self.wt = SafeThread(target=self.__worker).start()
        
    def set_tracking(self, HORIZONTAL=False, VERTICAL=True, DISTANCE=True, ROTATION=True):
        """
        Set tracking options
        Args:
            HORIZONTAL (bool, optional): Defaults to True.
            VERTICAL (bool, optional): Defaults to True.
            DISTANCE (bool, optional): Defaults to True.
        """

        self.use_vertical_tracking = VERTICAL
        self.use_horizontal_tracking = HORIZONTAL
        self.use_distance_tracking = DISTANCE
        self.use_rotation_tracking = ROTATION
        
    def onTracking(self):
        self.tracking = True
        
    def offTracking(self):
        self.tracking = False
        
    def isTracking(self):
        return self.tracking
        
    def process_frame(self, frame):
        # frame = cv2.resize()
        self.frame = frame
    
    def __worker(self):
        # time base
        self.ticker.wait(0.005)
        
        # process image, command tello
        if self.frame is not None and self.cycle_counter % self.cycle_activation == 0:
            dist = 0
            vy = 0
            vx, rx = 0, 0
            
            frame = self.frame.copy()
            
            tp = None
            det = None
            if self.tracking:
                tp, det = self.detect(frame)
            
            if det is not None and len(det) > 0:
                
                self.det = det
                self.tp = tp
                
                if self.track == False:
                    self.h, self.w = frame.shape[:2]
                    self.track = True
                    
                x_feedback = tp[0] / self.w
                y_feedback = tp[1] / self.h
                z_feedback = tp[4] / self.h
                x_control_effort, x_error = self.pid_x.control_effort(self.cx, x_feedback)
                y_control_effort, y_error = self.pid_y.control_effort(self.cy, y_feedback)
                z_control_effort, z_error = self.pid_z.control_effort_depth(self.cz, z_feedback)      
                # print("---------------")
                # print(x_control_effort)
                # print(y_control_effort)
                # print(z_control_effort)
                # print("---------------")
                          
                max_speed = self.tello.get_max_speed()
                    
                if self.use_horizontal_tracking:
                    rx = 0
                    vx = -int(x_control_effort * max_speed)
                    
                if self.use_rotation_tracking:
                    vx = 0
                    rx = -int(x_control_effort * max_speed)

                if self.use_vertical_tracking:
                    vy = int(y_control_effort * max_speed)
                
                if self.use_distance_tracking:
                    vz = int(z_control_effort * max_speed)
                    
                # Send Command to Tello
                leftright = vx
                fwdbackw = vz
                updown = vy
                yaw = rx
                
            else:
                leftright = 0
                fwdbackw = 0
                updown = 0
                yaw = 0
                self.det = None
            
            if self.tracking:   
                self.tello.updateVelocity(leftright, fwdbackw, updown, yaw)
        self.cycle_counter += 1
            
    def draw_detections(self,img):
        battery = self.tello.get_battery()
        
        if img is not None:

            h,w = img.shape[:2]
            battery_info = f"Battery: {battery}"
            tracking_info = f"Tracking: {self.isTracking()}"
            
            # Adjust font scale and thickness
            font_scale = 0.5
            thickness = 1
            
            cv2.putText(img, battery_info, (10, h-10), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 255), thickness, cv2.LINE_4)
            cv2.putText(img, tracking_info, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 255), thickness, cv2.LINE_4)

            if self.det is not None:            
                for val in self.det:
                    cv2.rectangle(img,(val[0],val[1]),(val[0]+val[2],val[1]+val[3]),[0,255,0],2)
                    cv2.circle(img,(self.tp[0],self.tp[1]),3,[0,0,255],-1)
                cv2.circle(img,(int(self.cx * self.w),int(self.cy * self.h)),4,[0,255,0],1)
                cv2.line(img,(int(self.cx * self.w),int(self.cy * self.h)),(self.tp[0],self.tp[1]),[0,255,0],2)
                
    # self.cx = w // 2
    # self.cy = h // 3