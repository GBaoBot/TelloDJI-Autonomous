from SafeThread import *
from BrainDetect import *
from Kalman import *
# from TelloMain import *
class BrainTrack(BrainDetect):
    def __init__(self, tello, MODEL="yolov8n.pt", CONFIDENCE=0.4, DETECT=0) -> None:
        super().__init__(MODEL, CONFIDENCE, DETECT)
        
        self.tello = tello
        
        # ticker for timebase
        self.ticker = threading.Event()
        
        # Kalman estimators
        self.kf = Kalman()
        self.kfarea= Kalman()
        
        #init 
        self.track = False
        self.frame = None
        self.det = None
        self.tp = None
        
        # tracking options
        self.use_vertical_tracking = True
        self.use_rotation_tracking = True
        self.use_horizontal_tracking = True
        self.use_distance_tracking = True
        
        # distance between object and drone
        self.dist_setpoint = 100
        self.area_setpoint = 13
        
        # processing frequency (to spare CPU time)
        self.cycle_counter = 1
        self.cycle_activation = 10
        
        # Kalman estimator scale factors
        self.kvscale = 6
        self.khscale = 4
        self.distscale = 3
        
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
        
    def process_frame(self, frame):
        self.frame = frame
    
    def __worker(self):
        
        # Time Base
        # self.ticker.wait(0.005)
        
        # process image, command tello
        if self.frame is not None and self.cycle_counter % self.cycle_activation == 0:
            dist = 0
            vy = 0
            vx, rx = 0, 0
            
            frame = self.frame.copy()
            
            tp, det = self.detect(frame)
            
            if len(det) > 0:
                self.det = det
                self.tp = tp
                
                if self.track == False:
                    h, w = frame.shape[:2]
                    self.cx = w // 2
                    self.cy = h // 2
                    self.kf.init(self.cx, self.cy)
                    
                    self.kfarea.init(1, tp[1])
                    
                    self.track = True
                    
                # process corrections, compute delta between two objects
                _,cp = self.kf.predictAndUpdate(self.cx,self.cy,True)

                # calculate delta over 2 axis
                mvx = -int((cp[0]-tp[0])//self.kvscale)
                mvy = int((cp[1]-tp[1])//self.khscale)
                
                if self.use_distance_tracking:
                    # use detection y value to estimate object distance
                    obj_y = tp[2]
                    _, ocp = self.kfarea.predictAndUpdate(1, obj_y, True)
                    dist = int((ocp[1]-self.dist_setpoint)//self.distscale)
                
                # Fill out variables to be sent in the tello command
                # don't combine horizontal and rotation
                if self.use_horizontal_tracking:
                    rx = 0
                    vx = mvx
                if self.use_rotation_tracking:
                    vx = 0
                    rx = mvx

                if self.use_vertical_tracking:
                    vy = mvy
                    
                # Send Command to Tello
                leftright = vx
                fwdbackw = -dist
                updown = vy
                yaw = rx
                
            else:
                leftright = 0
                fwdbackw = 0
                updown = 0
                yaw = 0
                self.det = None
            
            self.tello.updateVelocity(leftright, fwdbackw, updown, yaw)
        self.cycle_counter += 1
            
        
    def draw_detections(self,img):

        if img is not None:

            h,w = img.shape[:2]

            if self.det is not None:            
                for val in self.det:
                    cv2.rectangle(img,(val[0],val[1]),(val[0]+val[2],val[1]+val[3]),[0,255,0],2)
                    
                    cv2.circle(img,(self.tp[0],self.tp[1]),3,[0,0,255],-1)
                cv2.circle(img,(int(w/2),int(h/2)),4,[0,255,0],1)
                cv2.line(img,(int(w/2),int(h/2)),(self.tp[0],self.tp[1]),[0,255,0],2)

    
        
        