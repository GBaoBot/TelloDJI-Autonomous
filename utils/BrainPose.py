# STEP 1: Import the necessary modules.
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
from mediapipe import solutions
import mediapipe as mp
import cv2
import numpy as np
from ultralytics import YOLO

'''
This is just for testing
'''

class BrainPose_Mediapipe:
    def __init__(self):
        base_options = python.BaseOptions(model_asset_path='pose_landmarker_lite.task')

        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=True)
        self.detector = vision.PoseLandmarker.create_from_options(options)

    def draw_landmarks_on_image(self, rgb_image, detection_result):
        pose_landmarks_list = detection_result.pose_landmarks
        annotated_image = np.copy(rgb_image)

        # Loop through the detected poses to visualize.
        for idx in range(len(pose_landmarks_list)):
            pose_landmarks = pose_landmarks_list[idx]

            # Draw the pose landmarks.
            pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            pose_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
            ])
            solutions.drawing_utils.draw_landmarks(
            annotated_image,
            pose_landmarks_proto,
            solutions.pose.POSE_CONNECTIONS,
            solutions.drawing_styles.get_default_pose_landmarks_style())
        return annotated_image
    
    def runTest(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if ret:
                mp_frame = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
                mp_frame_np = mp_frame.numpy_view()
                mp_frame_np = np.copy(mp_frame_np)

                detection_result = self.detector.detect(mp_frame)

                frame_processed = self.draw_landmarks_on_image(frame, detection_result)

                cv2.imshow("frame", frame_processed)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
        cv2.destroyAllWindows()
   
 
class BrainPose_Yolov8:
    def __init__(self):
        self.detectorPose = YOLO('yolov8n-pose.pt')
        self.detectorPose.to('cuda')
        
    
    def runTestWithWebcam(self):
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            
            if not ret: continue
            
            result = self.detectorPose.track(frame, classes=[0] ,conf=0.5, persist=True, verbose=False)[0]
            # result = self.detectorPose.track(frame, classes=[0], conf=0.5, persist=True, verbose=False)[0]
            
            if len(result) != 0:
                obj = result[0]
                # print(self.isRaiseHand(obj))
                # try:
                id = obj.boxes.id.tolist()[0]
                print(id)
                # except Exception as e:
                    # print(f"Cannot extract id: {e}")
            
            frame = result.plot()
            
            cv2.imshow("frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
        cv2.destroyAllWindows()
        
        
    def runTestWithImage(self):
        path = r'C:\Users\GiaBao\Documents\VSC\Robot\TelloDJI-Autonomous\DroneTelloProject\Data\images.jpg'
        image = cv2.imread(path)
        
        result = self.detectorPose(image)[0]
        obj = result[0]
        # print(self.isRaiseHand(obj=obj))
        
        
        image = result.plot()        
        cv2.imshow('image', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    def isRaiseHand(self, obj):
        keyPoints = obj.keypoints.xy.tolist()[0]
        
        leftShoulder, rightShoulder = keyPoints[5:7]
        leftWrist, rightWrist = keyPoints[9:11]
        
        distLeft = leftShoulder[1] - leftWrist[1] 
        distRight = rightShoulder[1] - rightWrist[1]
        
        if (leftShoulder[1] != 0 and leftWrist[1] != 0 and distLeft > 5) or (rightShoulder[1] != 0 and rightWrist[1] != 0 and distRight > 5):
            return True
        return False
    
if __name__ == "__main__":
    pose = BrainPose_Yolov8()
    pose.runTestWithWebcam()