from ultralytics import YOLO
import cv2

# Load YOLO model
model = YOLO("yolov8n.pt")

# Load video
path = 'C:\\Users\\GiaBao\\Documents\\VSC\\Robot\\TelloDJI-Autonomous\\DroneTelloProject\\Data\\test.mp4'
cap = cv2.VideoCapture(path)

cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE)

objectChosen = False
idObject = 0
classObject = 0
# Read frames from the video
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print('Cannot read frame!')
        break

    # Perform tracking

    # Get the tracking results
    # tracked_objects = results[0]
    
    # results = model.track(frame)  # Track only class 0 (person), change as needed
    
    if not objectChosen:
        results = model.track(frame, persist=True)  # Track only class 0 (person), change as needed
        objs = results[0]
        
        print("Please choose object to track")
        for obj in objs:
            print(f'Object {obj.boxes.id.item()}: {obj.names[obj.boxes.cls.item()]} with class: {obj.boxes.cls.item()}')
        idObject = int(input("Enter the object ID to track: "))
        classObject = int(objs[idObject].boxes.cls.item())        
        objectChosen = True
        # wait for user to input
            
    if objectChosen:
        results = model.track(frame, classes=[classObject], persist=True)
        
    frame = results[0].plot()
    # # Draw bounding boxes and class IDs on the frame
    # for obj in tracked_objects:
    #     box = obj.boxes
    #     # class_id = obj.cls
    #     x1, y1, x2, y2 = box.xyxy
    #     cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    #     # cv2.putText(frame, f"ID: {class_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    # print(results[0][0].names)
    # break
    # Display the frame
    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
