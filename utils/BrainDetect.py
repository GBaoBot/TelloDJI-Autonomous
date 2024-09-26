from ultralytics import YOLO
import cv2

# from mediapipe.tasks import python
# from mediapipe.tasks.python import vision
# from mediapipe.framework.formats import landmark_pb2
# from mediapipe import solutions


class BrainDetect:
    def __init__(self, CONFIDENCE=0.5) -> None:

        # Setup Model?
        self.didSetUpModel = False

        self.conf = CONFIDENCE

        # Users' inputs
        self.clickCoor = (0, 0)

        # Model Object Detection
        self.model = None

        # Result of Detecting
        self.tp = []
        self.detections = []
        self.idTracking = -1

    def process_clickCoor(self, clickCoor):
        self.clickCoor = clickCoor
        # print("Did process clickCoor")

    def detect(self, frame):
        """
        return tp, detections
        """
        if not self.didSetUpModel:
            self.setUpYOLOv8()
            self.didSetUpModel = True
        return self.detectWithYOLOv8(frame)

    # YOLOv8
    def setUpYOLOv8(self, MODEL=r"models/yolov8m-face.pt"):
        self.model = YOLO(MODEL)
        self.model.to("cuda")

    def detectWithYOLOv8(self, frame):

        result = self.model.track(frame, conf=self.conf, persist=True, verbose=False)[0]
        tp, detections = self.processResultYOLOv8(frame, result)

        return tp, detections

    def processResultYOLOv8(self, frame, result):
        h, w = frame.shape[:2]
        tp = []
        detections = []

        if len(result) != 0:
            obj = None
            if self.clickCoor != (0, 0):
                x, y = self.clickCoor
                for objDetected in result:
                    x1, y1, x2, y2 = objDetected.boxes.xyxy[0].tolist()
                    if x1 <= x <= x2 and y1 <= y <= y2:
                        obj = objDetected
                        # self.clickCoor = (0, 0)
                        # print("Did set it back 0-0")
                        break
            elif self.idTracking != -1:
                print("---------------")
                print(self.idTracking)
                print("---------------")
                for objDetected in result:
                    try:
                        idDetected = objDetected.boxes.id.tolist()[0]
                        if idDetected == self.idTracking:
                            obj = objDetected
                            break
                    except Exception as e:
                        print(f"Cannot extract id: {e}")
                        break

            if obj is not None:
                try:
                    self.idTracking = obj.boxes.id.tolist()[0]
                except Exception as e:
                    print(f"Object does not have id: {e}")

                # if len(result) != 0:
                # id = obj.boxes.id.item()
                # Box
                box_xyxy = obj.boxes.xyxy[0].tolist()  # [x1, y1, x2, y2]
                box_xyxy = [int(x) for x in box_xyxy]
                box_xywh = [
                    box_xyxy[0],
                    box_xyxy[1],
                    box_xyxy[2] - box_xyxy[0],
                    box_xyxy[3] - box_xyxy[1],
                ]
                detections.append(box_xywh)

                # Area ratio
                area_det = detections[0][2] * detections[0][3]
                tp = [
                    detections[0][0] + detections[0][2] // 2,
                    detections[0][1] + detections[0][3] // 2,
                    area_det,
                    detections[0][2],
                    detections[0][3],
                ]
        return tp, detections

    def draw_detections(self, det, img, COLOR=[0, 255, 0]):
        for d in det:
            cv2.rectangle(img, (d[0], d[1]), (d[0] + d[2], d[1] + d[3]), COLOR, 2)

    def detect_and_draw(self, img):
        _, det = self.detect(img)
        # print(det)
        self.draw_detections(det, img)

    def draw_landmarks_on_image(self, rgb_image, detection_result):
        pose_landmarks_list = detection_result.pose_landmarks
        annotated_image = self.np.copy(rgb_image)

        # Loop through the detected poses to visualize.
        for idx in range(len(pose_landmarks_list)):
            pose_landmarks = pose_landmarks_list[idx]

            # Draw the pose landmarks.
            pose_landmarks_proto = self.landmark_pb2.NormalizedLandmarkList()
            pose_landmarks_proto.landmark.extend(
                [
                    self.landmark_pb2.NormalizedLandmark(
                        x=landmark.x, y=landmark.y, z=landmark.z
                    )
                    for landmark in pose_landmarks
                ]
            )
            self.solutions.drawing_utils.draw_landmarks(
                annotated_image,
                pose_landmarks_proto,
                self.solutions.pose.POSE_CONNECTIONS,
                self.solutions.drawing_styles.get_default_pose_landmarks_style(),
            )
        return annotated_image
