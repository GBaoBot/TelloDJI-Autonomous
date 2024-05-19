from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt


# Load model
model = YOLO("yolov8n.pt")

# Load video
# path = '/home/notomo/Documents/VSC/Robot/DroneTelloProject/Data/test.mp4'
path = '/home/notomo/Documents/VSC/Robot/DroneTelloProject/Data/1030_AT_puppies_feat.jpg'
# cap = cv2.VideoCapture(path)
img = cv2.imread(path)

cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE)

# Read frames
# while cap.isOpened():
# ret, frame = cap.read()

# if not ret:
#     print('Can not Read Frame!')
#     break

result = model.predict(img, classes=[0])
# print(result[0].boxes.xyxy[0])
print(result[0].names)

frame_ = result[0].plot()

cv2.imshow('frame', frame_)

# if cv2.waitKey(1) & 0xFF == ord('q'):
#     break

# Wait for a key press indefinitely
cv2.waitKey(0)

# Close all OpenCV windows
cv2.destroyAllWindows()
    