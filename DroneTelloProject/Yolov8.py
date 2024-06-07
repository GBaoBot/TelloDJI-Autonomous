from ultralytics import YOLO
import cv2

# Load YOLO model
model = YOLO("yolov8n.pt")
# model.to('cuda')

# Load video
path = 'C:\\Users\\GiaBao\\Documents\\VSC\\Robot\\TelloDJI-Autonomous\\TEST\\DroneTelloProject\\Data\\1030_AT_puppies_feat.jpg'
cap = cv2.VideoCapture(0)
cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Cannot read frames!!")
        break
    
    # Process frame
    frame = cv2.flip(frame, 1)

    results = model.track(frame, tracker="botsort.yaml", persist=True, verbose=False)
    # print(results[0][0].boxes.xyxy)
    detected_frame = results[0].plot()
    cv2.imshow('frame', detected_frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()