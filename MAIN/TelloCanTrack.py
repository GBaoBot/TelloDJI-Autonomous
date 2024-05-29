from ObjectTrack import *
from TelloBase import *
import signal


    
if __name__ == "__main__":
    # signal handler
    def signal_handler(sig, frame):
        raise Exception

    # capture signals
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    tello = TelloBase(speed=10)
    
    # Delay time for processing frame
    processWaitTime = 1
    
    # Set up
    tello.connect()
    tello.cameraOn()
    
    trackMethod = ObjectTrack(tello=tello)
    trackMethod.set_tracking()
    while True:
        try:
            frame = tello.getFrame()
            
            # wait for valid frame
            if frame is None: continue
            
            framehud = frame.copy()
            
            trackMethod.process_frame(frame)
            
            k = cv2.waitKey(processWaitTime)
        except Exception:
            tello.tello.land()
            trackMethod.stopTrack()
            tello.cameraOff()
            break
        
        trackMethod.draw_detections(framehud)
        cv2.imshow("TelloCamera", framehud)
        
        if k == ord('q'):
            tello.tello.land()
            trackMethod.stopTrack()
            tello.cameraOff()
            break
        
        if k == ord('l'):
            tello.tello.land()
            break
        
        if k == ord('t'):
            tello.tello.takeoff()
            break
        
    cv2.destroyAllWindows()