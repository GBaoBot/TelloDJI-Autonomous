import cv2
import numpy as np
from djitellopy import tello
import time

Drone = tello.Tello()
Drone.connect()
print(Drone.get_battery())

Drone.streamon()
Drone.takeoff()
Drone.send_rc_control(0,0,25,0)
time.sleep(2.2)

w,h=360,240
fbRange=[6200,6800]
pid = [0.4,0.4,0]
pError=0

def findFace(img):
    # cascadePath = r"C:\Users\cheeh\OneDrive\Desktop\Programming Stuff\Tello_Drone_Project\Resources\Images\haarcascade_frontalface_default.xml"
    cascadePath = ""
    faceCascade = cv2.CascadeClassifier(cascadePath)
    if faceCascade.empty():
        print("Error loading cascade file. Check the file path.")
        exit()
    imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) #this line will convert image to gray
    faces = faceCascade.detectMultiScale(imgGray,1.2,8)

    myFaceListC=[] #my face at the center
    myFaceListArea=[]

    for(x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
        #0,0,255 is the rbg format, meaning red
        #2 at the end means the thickness of the frame
        cx=x+w//2
        cy=y+h//2
        area=w*h
        cv2.circle(img,(cx,cy),5,(0,255,0),cv2.FILLED)
        #5 means the radius
        #0,255,0 means green
        #cv2.FILLED means the dot should be filled
        myFaceListC.append([cx,cy])
        myFaceListArea.append(area)
    
    if len(myFaceListArea)!=0:
        i=myFaceListArea.index(max(myFaceListArea))
        return img,[myFaceListC[i],myFaceListArea[i]]
    else:
        return img,[[0,0],0]

def trackFace(info,w,pid,pError):
    x,y=info[0]
    area=info[1]
    fb=0
    error=x-w//2
    speed = pid[0]*error+pid[1]*(error-pError)
    speed=int(np.clip(speed,-100,100))
    if area>fbRange[0] and area<fbRange[1]:
        fb=0
    elif area>fbRange[1]:
        fb=-20
    elif area<fbRange[0] and area != 0:
        fb=20
    
    #there's a bug here, if area = 0, which means it detects nothing, if will go forward also
    #to solve this, we write area != 0
    if x==0:
        speed=0
        error=0
    #print(speed,fb)
    Drone.send_rc_control(0,fb,0,speed)
    return error

#cap=cv2.VideoCapture(0)
#cap is for laptop webcam testing purpose
#if don't have multiple webcams, most probably is number 0

while True:
    #_, img = cap.read()
    img = Drone.get_frame_read().frame #name the picture captured img
    img=cv2.resize(img,(w,h))
    img,info = findFace(img)
    pError = trackFace(info,w,pid,pError)
    print("Center: ",info[0],"Area: ",info[1])
    cv2.imshow("Output",img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        Drone.land()
        break