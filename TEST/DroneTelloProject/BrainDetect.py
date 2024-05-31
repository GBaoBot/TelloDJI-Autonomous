from ultralytics import YOLO
import cv2

class BrainDetect:
    def __init__(self, MODEL="yolov8n.pt", CONFIDENCE=0.6, DETECT=0) -> None:
        
        # Model
        self.model = YOLO(MODEL)
        self.model.to('cuda')
        
        self.conf = CONFIDENCE
        self.clsDetect = DETECT
        
    def detect(self, frame):
        
        detections = []
        tp =[]
        
        h,w = frame.shape[:2]
        result = self.model.track(frame, classes=[self.clsDetect], conf=self.conf, persist=True)[0]
        # obj = result[0] # Need to figure out how to make drone "choose" a consistent object
        
        for obj in result:
        
            if self.clsDetect == 0:

                if len(result) != 0:
                    # id = obj.boxes.id.item()
                    # Box
                    box_xyxy = obj.boxes.xyxy[0].tolist() # [x1, y1, x2, y2]
                    box_xyxy = [int(x) for x in box_xyxy]
                    box_xywh = [box_xyxy[0], box_xyxy[1], box_xyxy[2] - box_xyxy[0], box_xyxy[3] - box_xyxy[1]]
                    detections.append(box_xywh)
                    
                    # Area ratio
                    area_frame = w*h
                    area_det = detections[0][2] * detections[0][3]
                    area_ratio = int((area_det/area_frame)*1000)
                    tp = [detections[0][0] + detections[0][2]//2, detections[0][1] + detections[0][3]//3, area_ratio]
                    
            else:
                box_xyxy = obj.boxes.xyxy[0].tolist() # [x1, y1, x2, y2]
                box_xyhw = [box_xyxy[0], box_xyxy[1], box_xyxy[2] - box_xyxy[0], box_xyxy[3] - box_xyxy[1]]
                detections.append(box_xyhw)
                tp = [detections[0][0] + detections[0][2]//2, detections[0][1] + detections[0][3]//2, detections[0][3]]
            
        return tp, detections
    
    def draw_detections(self,det,img,COLOR=[0,255,0]):
        """
        Draw detections

        Args:
            det ([type]): list of detected faces
            img ([type]): image
            COLOR (list, optional): box color. Defaults to [0,255,0].
        """

        for d in det:
            cv2.rectangle(img, (d[0], d[1]), (d[0] + d[2], d[1] + d[3]), COLOR, 2)
            
            
    def detect_and_draw(self,img):
        """
        Draw detection on an image
        Args:
            img ([type]): image to draw the detections
        """ 
        _, det = self.detect(img)
        # print(det)
        self.draw_detections(det,img)

            
            
        