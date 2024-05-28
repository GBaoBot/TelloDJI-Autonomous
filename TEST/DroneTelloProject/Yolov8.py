from ultralytics import YOLO
import cv2

# Load YOLO model
model = YOLO("yolov8n.pt")
model.to('cuda')

# Load video
path = 'C:\\Users\\GiaBao\\Documents\\VSC\\Robot\\TelloDJI-Autonomous\\DroneTelloProject\\Data\\test.mp4'
cap = cv2.VideoCapture(0)
cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Cannot read frames!!")
        break
    
    # Process frame
    frame = cv2.flip(frame, 1)

    results = model.track(frame, persist=True)
    detected_frame = results[0].plot()
    cv2.imshow('frame', detected_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()