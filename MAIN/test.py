# from djitellopy import Tello
import threading
import cv2

# Function to continuously capture and display frames
def video_stream():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        frame = cv2.resize(frame, (480, 480))
        if frame is not None: 
            print("Received")
            cv2.imshow("frame", frame)
        else:
            print("Cannot get frame!")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

# Create and start the video streaming thread
video_thread = threading.Thread(target=video_stream)
video_thread.start()

# The rest of your Tello drone code
# drone = Tello()
# drone.connect()
# drone.streamon()  
# print(drone.get_battery())

# Uncomment below lines if you want to use the Tello's stream
# cv2.namedWindow("frame", cv2.WINDOW_AUTOSIZE)
# cv2.resizeWindow('frame', 480, 480)

# while True:
#     frame = drone.get_frame_read().frame  
#     if frame is not None: 
#         print("Received")
#         cv2.imshow("frame", frame)
#     else:
#         print("Cannot get frame!")

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cv2.destroyAllWindows()
# drone.streamoff()
