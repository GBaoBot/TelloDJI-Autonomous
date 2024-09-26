from djitellopy import Tello
from ultralytics import YOLO
import cv2

# Connect to Tello
tello = Tello()
tello.connect()

# Start video stream
tello.streamon()

# Load YOLO model
path = r"models/yolov8n-face.pt"
model = YOLO(path)
model.to("cuda")

cv2.namedWindow("frame", cv2.WINDOW_AUTOSIZE)

while True:
    # Read frame from Tello
    frame = tello.get_frame_read().frame

    if frame is None:
        print("Cannot read frames!!")
        break

    print("Frame size:", frame.shape)  # {{ edit_1 }}

    # Process frame
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (320, 240))
    frame = cv2.flip(frame, 1)

    results = model.track(frame, tracker="botsort.yaml", persist=True, verbose=False)

    # Print positions of detected objects
    for result in results[0].boxes:
        print("Detected object position:", result.xyxy)  # {{ edit_2 }}

    detected_frame = results[0].plot()
    cv2.imshow("frame", detected_frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

tello.streamoff()
cv2.destroyAllWindows()
