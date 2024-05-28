from TelloDJI import *
import numpy as np

class TelloTrack(TelloDJI):
    def __init__(self, speed=10):
        super().__init__(speed)
        self.should_stop = False
        self.objectChosen = False
        self.idObjectToTrack = 0

    
    def suggest_action_when_tracking(self, frame, bounding_box):  
        x1, y1, x2, y2 = bounding_box 
        w = x2 - x1 
        h = y2 - y1 
        cx = x1 + w // 2
        cy = y1 + h // 2 
        
        fh, fw, _ = frame.shape
        print(fh, fw)
        fcx = fw // 2
        fcy = fh // 2

        error_x = cx - fcx
        error_y = fcy - cy

        margin = 0.3
        desired_width = fw // 3  # Desired width for the bounding box
        # desired_height = fh // 3  # Desired height for the bounding box

        width_margin = 0.3
        # height_margin = 0.5
        
        ## 720 960

        # Forward/Backward movement based on width
        if w < desired_width * (1 - width_margin):
            print('FORWARD (Width)')
            self.for_back_velocity = (self.speed)
        elif w > desired_width * (1 + width_margin):
            print('BACKWARD (Width)')
            self.for_back_velocity = -(self.speed)
        # Forward/Backward movement based on height
        # elif h < desired_height * (1 - height_margin):
        #     print('FORWARD (Height)')
        #     self.for_back_velocity = (self.speed)
        # elif h > desired_height * (1 + height_margin):
        #     print('BACKWARD (Height)')
        #     self.for_back_velocity = -(self.speed)
        else:
            self.for_back_velocity = 0
        
        
        
        if abs(error_x) > fcx * margin:  # 10% margin
            if error_x < 0:
                print('LEFT')
                self.yaw_velocity = -self.speed
            else:
                print('RIGHT')
                self.yaw_velocity = self.speed
        else:
            print('STOP')
            self.yaw_velocity = 0

        if abs(error_y) > fcy * margin:  # 10% margin
            if error_y > 0:
                print('UP')
                self.up_down_velocity = self.speed
            else:
                print('DOWN')
                self.up_down_velocity = -self.speed
        else:
            print('STOP')
            self.up_down_velocity = 0
          
        
        return 
    

    def track_human(self):
        try:
            self.connect()
            self.camera_on()
            self.tello.takeoff()

            model = self.init_model()
            cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE)
            cv2.resizeWindow('frame', 240, 240)

            listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
            listener.start()

            result = None
            while not self.should_stop:
                frame = self.get_frame()
                
                result = model.track(frame, classes=[0], persist=True)
                # if not self.objectChosen:
                #     print("Please choose object to track")
                #     for obj in result[0]:
                #         print(f'Object {int(obj.boxes.id.item())}: {obj.names[obj.boxes.cls.item()]} - class {obj.boxes.cls.item()}')
                #     idObject = int(input("Enter the object ID to track: "))
                    
                frame_ = result[0].plot()
                # frame_ = cv2.cvtColor(frame_, cv2.COLOR_BGR2RGB)
                cv2.imshow('frame', frame_)

                if len(result[0].boxes.xyxy) != 0:
                    box = result[0].boxes.xyxy[0].tolist() 
                    self.suggest_action_when_tracking(frame, box)
                else:
                    self.stop_moving()

                self.update()
                # time.sleep(0.1)
                if cv2.waitKey(1) & 0xFF == 27:
                    break

            self.tello.land()

        except Exception as e:
            print(f"An error occurred: {e}")
            self.tello.land()
        finally:
            listener.stop()
            listener.join()
            cv2.destroyAllWindows()
            self.tello.streamoff()
            self.tello.end()
            
    def on_press(self, key):
        try:
            if key == keyboard.Key.up:  # forward 
                self.for_back_velocity = self.speed
            elif key == keyboard.Key.down:  # backward 
                self.for_back_velocity = -self.speed
            elif key == keyboard.Key.left:  # left 
                self.left_right_velocity = -self.speed
            elif key == keyboard.Key.right:  # right 
                self.left_right_velocity = self.speed
            elif hasattr(key, 'char'):
                if key.char == 'w':  # up 
                    self.up_down_velocity = self.speed
                elif key.char == 's':  # down 
                    self.up_down_velocity = -self.speed
                elif key.char == 'a':  # yaw counter clockwise 
                    self.yaw_velocity = -self.speed
                elif key.char == 'd':  # yaw clockwise 
                    self.yaw_velocity = self.speed
            self.send_rc_control = True
        except AttributeError:
            print(f'Special key {key} pressed')

    def on_release(self, key):
        try:
            if key in {keyboard.Key.up, keyboard.Key.down}:  # zero forward/backward
                self.for_back_velocity = 0
            elif key in {keyboard.Key.left, keyboard.Key.right}:  # zero left/right
                self.left_right_velocity = 0
            elif hasattr(key, 'char'):
                if key.char in {'w', 's'}:  # zero up/down
                    self.up_down_velocity = 0
                elif key.char in {'a', 'd'}:  # zero yaw
                    self.yaw_velocity = 0
                elif key.char == 't':  # takeoff
                    self.tello.takeoff()
                    self.send_rc_control = True
                elif key.char == 'l':  # land
                    self.tello.land()
                    self.send_rc_control = False
        except AttributeError:
            print(f'Special key {key} released')
        if key == keyboard.Key.esc:
            self.tello.land()
            self.send_rc_control = False
            self.should_stop = True
            return False
        
        
def try_track():
    drone = TelloTrack(30)
    drone.track_human()
    
if __name__ == '__main__':
    try_track()