from pynput import keyboard


class BrainControl():
    def __init__(self, tello, speed):
        self.tello = tello
        self.speed = speed
        self.should_stop = False
        
        self.pspeed = 1
        
        # Velocity
        self.for_back_velocity = 0 
        self.left_right_velocity = 0 
        self.up_down_velocity = 0 
        self.yaw_velocity = 0 
        
        # Keyboard
        self.listener = None
        
    def startReadFromKeyboard(self):
        print("Started Keyboard!")
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()
        
        
    def stopReadFromKeyboard(self):
        print("Stopped Keyboard!")
        self.listener.stop()
    
        
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
            self.tello.updateVelocity(self.left_right_velocity, self.for_back_velocity, self.up_down_velocity, self.yaw_velocity)
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
                    self.tello.tello.takeoff()
                    return
                elif key.char == 'l':  # land
                    self.tello.tello.land()
                    return
            self.tello.updateVelocity(self.left_right_velocity, self.for_back_velocity, self.up_down_velocity, self.yaw_velocity)
        except AttributeError:
            print(f'Special key {key} released')
