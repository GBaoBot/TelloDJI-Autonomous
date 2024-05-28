import cv2
import time
from pynput import keyboard
from TelloDJI import TelloDJI

class TelloControl(TelloDJI):
    def __init__(self, speed=10):
        super().__init__(speed)
        self.should_stop = False

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

    def control(self):
        self.connect()
        self.camera_on()
        
        cv2.namedWindow('frame')
        cv2.resizeWindow('frame', 480, 480)

        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()

        try:
            while not self.should_stop:
                frame = self.frame_read.frame
                if frame is not None:
                    cv2.imshow('frame', frame)
                else:
                    print("No frame!!!")

                if cv2.waitKey(1) & 0xFF == 27:
                    break

                self.update()
                # time.sleep(0.1)  # Update rate of 10 times per second
        finally:
            listener.stop()
            listener.join()
            cv2.destroyAllWindows()
            self.tello.streamoff()
            self.tello.end()

def try_control():
    drone = TelloControl(50)
    drone.control()

if __name__ == '__main__':
    try_control()
