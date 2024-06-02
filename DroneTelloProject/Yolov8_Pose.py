from ultralytics import YOLO
import cv2

model = YOLO("yolov8n-pose.pt")  # Load model
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    results = model(frame)
    # Check if the keypoints attribute is present in the results
    if hasattr(results[0], 'keypoints'):
        # Access the keypoints for the first detected object
        keypoints = results[0].keypoints
        
        keypoints_numpy = keypoints.xyn.cpu().numpy()[0]
        print(keypoints_numpy)
    else:
        print("No keypoints attribute found in the results.")
    
    frame = results[0].plot()
    cv2.imshow('frame', frame)

    if cv2.waitKey(0) & 0xFF == ord('q'):
        break      
        
cv2.destroyAllWindows()
