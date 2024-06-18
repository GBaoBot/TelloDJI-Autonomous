# TelloDJI-Autonomous

I consulted from this GitHub: https://github.com/fvilmos/tello_object_tracking/tree/master

In this project, I used a DJI Tello EDU drone to do task of object following. Currently, there are 2 main modes the drone can operate: Control and Tracking. You can check the result in folder "videos".

### Run
To run this code, paste this command line in terminal (or Powershell):
```
python TelloMain.py
```
After running, user can choose modes which are shown in the terminal, please follow instruction shown in the terminal.

### Modes

* Control Mode (1): Users manually control the drone with keyboard. (For example: press 't' to take off, 'l' to land, 'w' to fly up, etc.)
* Tracking Mode (2): The drone detect people in frame and start to follow one of them right after he raises hand. When he put his hand down, it still follows him unless there is someone else raising their hand. Another way is that the drone track person who was clicked on by user, using mouse. These 2 types of tracking can be selected at the beginning. This tracking mode can be turned on or off by pressing 'm' on keyboard.

Libraries and Models:
* To control the DJI Tello Drone, the library "djitellopy" was used due to its friendly API. OpenCV was used to stream video frames received from Tello Drone.
* To track people in frame, Yolov8-pose was used due to its fast and accuracy, along with Kalman Filter to improve the performance.

Future:
* I will try to make it work with different inputs. It can be prompt from user (Example: "Fly up and move forward but not too fast"). Or it can receive audio from micro on laptop. And users also should be allowed to control drone with hand gestures.
* In terms of connection and control, I will try to apply PID control, and improve the quality of video stream.
