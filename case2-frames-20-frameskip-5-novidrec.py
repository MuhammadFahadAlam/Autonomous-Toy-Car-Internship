import numpy as np 
import cv2
#from matplotlib import pyplot as plt
import time
import urllib.request
from imutils.video import WebcamVideoStream

def GetMask(img):

    width=img.shape[0]
    height = img.shape[1]

    img = cv2.resize(img, (0,0), fx=0.25, fy=0.25)

    smoothed = cv2.bilateralFilter(img,19,150,100)

    gray = cv2.cvtColor(smoothed,cv2.COLOR_BGR2GRAY)
    
    _ , thresh = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY + cv2.THRESH_OTSU) 
  
    kernel = np.ones((3,3),np.uint8)

    sure_bg = cv2.erode(thresh,kernel,iterations=10)

    contours, hierarchy = cv2.findContours(sure_bg,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
  
    mask = np.zeros(gray.shape, np.uint8)
  
    c = max(contours, key = cv2.contourArea)

    cv2.drawContours(mask, [c],-1 , (255,255,255), cv2.FILLED)

    mask = cv2.resize(mask, (height,width ))

    return mask

def decision(image):
    global state
    width = 100
    height = 125

    mask = image.copy()
    #imageMask = image.copy()
    
        
    carBox = mask[ (mask.shape[0]) - height: , width : ]

    left = carBox[:, : carBox.shape[1]//2]
    right = carBox[:, carBox.shape[1]//2 : ]

    sumLeftWhite = np.sum(left==255)
    sumRightWhite = np.sum(right==255)
    sumLeftBlack = np.sum(left==0)
    sumRightBlack = np.sum(right==0)
    
    print(f'sumLeftWhite:{sumLeftWhite},sumRightWhite:{sumRightWhite},sumLeftBlack:{sumLeftBlack},sumRightBlack:{sumRightBlack}')

    
    if (sumRightBlack >= sumRightWhite and sumLeftBlack >= sumLeftWhite):
        if state[-1] != 'b':
            urllib.request.urlopen(root_url+"/?State=B")
            state.append('b')
            print(root_url+"/?State=B")
    else:
        if sumLeftWhite > sumRightWhite:
            if state[-1] != 'l':
                urllib.request.urlopen(root_url+"/?State=G")
                print(root_url+"/?State=G")
                state.append('l')

 
        elif sumLeftWhite < sumRightWhite:
            if state[-1] != 'r':
                urllib.request.urlopen(root_url+"/?State=I")
                print(root_url+"/?State=I")
                state.append('r')

        else:
            if state[-1] != 'f':
                if state[-1] == 'r':
                    urllib.request.urlopen(root_url+"/?State=PL")
                    print('PINGED LEFT')
                elif state[-1] == 'l':
                    urllib.request.urlopen(root_url+"/?State=PR")
                    print('PINGED RIGHT')
                urllib.request.urlopen(root_url+"/?State=F")
                state.append('f')
                print(root_url+"/?State=F")


#--------------------------------------------------------------------------------------------------#

root_url = "http://192.168.4.1"  # ESP's url, ex: http://192.168.102 (Esp prints it to serial console when connected to wifi)
ip_webcam_url = 'https://192.168.4.2:8080/video'
#ip_webcam_url = 'https://192.168.18.137:8080/video'

demoVideoName = 'demoVideo3'
outputVideoName = 'liveDriveVideo30'

state = ['s']

count = 0;

# number of frames to skip
FramesToSkip = 2


cap = WebcamVideoStream(src=ip_webcam_url).start()

time.sleep(1)

while(True):    

        
    if (count % FramesToSkip == 0):
        frame = cap.read()
        if frame is None:
            break
        #start = time.process_time()
        #print(time.process_time() - start)
        getmask = GetMask(frame)
        decision(getmask)


    count += 1

cap.stop()

