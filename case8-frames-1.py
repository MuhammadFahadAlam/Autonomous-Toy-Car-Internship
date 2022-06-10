import numpy as np 
import cv2
#from matplotlib import pyplot as plt
import time
import urllib.request
from imutils.video import WebcamVideoStream

def GetMask(img):

  # Perform Bilateral Blur on the image to remove noise from the image
    width=img.shape[0]
    height = img.shape[1]

    img = cv2.resize(img, (0,0), fx=0.25, fy=0.25)

    smoothed = cv2.bilateralFilter(img,19,150,100)

  # Converting image to gray scale

    gray = cv2.cvtColor(smoothed,cv2.COLOR_BGR2GRAY)
  
  # Perform basic Thresholding on the gray scale image
  
    _ , thresh = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY + cv2.THRESH_OTSU) 
  
  # Making kernal for Morphological Operations which is generally a square with all ones  

    kernel = np.ones((3,3),np.uint8)

    sure_bg = cv2.erode(thresh,kernel,iterations=10)
  
  # Finding Contours in the pre-processed image

    contours, hierarchy = cv2.findContours(sure_bg,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
  
  # Initializing mask of same shape as the image with all zeros
  
    mask = np.zeros(gray.shape, np.uint8)
  
  # storing contour with greatest area in a variable.
  
    c = max(contours, key = cv2.contourArea)

  # Draw Contours on the image

    cv2.drawContours(mask, [c],-1 , (255,255,255), cv2.FILLED)
  
  # Anding mask and image to get the flooring area of the image

  # mask = cv2.bitwise_and(img,mask,mask=None)

  #plt.imshow(mask,cmap='gray')
    mask = cv2.resize(mask, (height,width ))
  #plt.imshow(mask,cmap='gray')
    return mask

def decision(image):
    global state
    width = 200
    height = 250

    mask = image.copy()
    imageMask = image.copy()
    
    
    #carBox = mask[ (mask.shape[0]) - height: ,(mask.shape[1]//2) - width//2: (mask.shape[1]//2) + width//2]
    
    carBox = mask[ (mask.shape[0]) - height: , width : ]
    
    # Make Border around ROI
    imageMask[ (mask.shape[0]) - height: (mask.shape[0]) - height + 1  , width : ] = 200
    imageMask[ (mask.shape[0]) - height: , width : width + 1 ] = 180
    img = cv2.cvtColor(imageMask,cv2.COLOR_GRAY2BGR)

    left = carBox[:, : carBox.shape[1]//2]
    right = carBox[:, carBox.shape[1]//2 : ]

    sumLeftWhite = np.sum(left==255)
    sumRightWhite = np.sum(right==255)
    sumLeftBlack = np.sum(left==0)
    sumRightBlack = np.sum(right==0)
    
    print(f'sumLeftWhite:{sumLeftWhite},sumRightWhite:{sumRightWhite},sumLeftBlack:{sumLeftBlack},sumRightBlack:{sumRightBlack}')

    flag = True
    
    if (sumRightBlack >= sumRightWhite and sumLeftBlack >= sumLeftWhite):
        try:
            #urllib.request.urlopen(root_url+"/?State=B")
            #print(root_url+"/?State=S")
            #time.sleep(0.2)
            if state[-1] != 'b':
                urllib.request.urlopen(root_url+"/?State=B")
                state.append('b')
            print(root_url+"/?State=B")
            cv2.putText(img, 'B SLW:{} SRW:{} SLB:{} SRB:{}'.format(sumLeftWhite,sumRightWhite,sumLeftBlack,sumRightBlack), (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)
            #state.append('b')
        except:
            flag = False
            #imageMask = 'error'
            #return imageMask
        #return imageMask
    else:
        if sumLeftWhite > sumRightWhite:
            try:
                if state[-1] != 'l':
                    urllib.request.urlopen(root_url+"/?State=G")
                    print(root_url+"/?State=G")
                    state.append('l')
                cv2.putText(img, 'L SLW:{} SRW:{} SLB:{} SRB:{}'.format(sumLeftWhite,sumRightWhite,sumLeftBlack,sumRightBlack), (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)

            except:
                #imageMask = 'error'
                #return imageMask
                flag = False
            
            #return imageMask
 
        elif sumLeftWhite < sumRightWhite:
            try:
                if state[-1] != 'r':
                    urllib.request.urlopen(root_url+"/?State=I")
                    print(root_url+"/?State=I")
                    state.append('r')
                cv2.putText(img, 'R SLW:{} SRW:{} SLB:{} SRB:{}'.format(sumLeftWhite,sumRightWhite,sumLeftBlack,sumRightBlack), (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)

            except:
                #imageMask = 'error'
                #return imageMask
                flag = False
            
            #return imageMask

        else:
            try:
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
                cv2.putText(img, 'F SLW:{} SRW:{} SLB:{} SRB:{}'.format(sumLeftWhite,sumRightWhite,sumLeftBlack,sumRightBlack), (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)

                #sendRequest(root_url+"/?State=S")
            except:
                #imageMask = 'error'
                #return imageMask
                flag = False
            
            #return imageMask

    if flag == True:
        #img = cv2.cvtColor(imageMask,cv2.COLOR_GRAY2BGR)
        #stacked = np.hstack((image, img))
        #print(stacked.shape)
        return img #stacked
    else:
        
        return None

#--------------------------------------------------------------------------------------------------#

root_url = "http://192.168.4.1"  # ESP's url, ex: http://192.168.102 (Esp prints it to serial console when connected to wifi)
ip_webcam_url = 'https://192.168.4.2:8080/video'
#ip_webcam_url = 'https://192.168.18.137:8080/video'

demoVideoName = 'demoVideo3'
outputVideoName = 'liveDriveVideo21'

state = ['s']

#def sendRequest(url):
    #print(url)
    #urllib.request.urlopen(url) # send request to ESP



#cap = cv2.VideoCapture(demoVideoName+'.mp4')

fourcc = cv2.VideoWriter_fourcc(*'MP4V')
#out = cv2.VideoWriter(outputVideoName +'.mp4',fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))
out = cv2.VideoWriter(outputVideoName +'.mp4',fourcc, 1.0, (1280,720))

count = 0;

# number of frames to skip
FramesToSkip = 10


cap = WebcamVideoStream(src=ip_webcam_url).start()

time.sleep(1)

while(True):    
    
    frame = cap.read()

    # if a frame is not read correctly or there are no more frames to be read the 
    #if not ret:
        #print('Done Creating Video')
        #sendRequest(root_url+"/?State=S")
        #try:
         #   urllib.request.urlopen(root_url+"/?State=S")
        #except:
         #   break
    if frame is None:
        break
        
    #if (count % FramesToSkip == 0):
        #start = time.process_time()
        #print(time.process_time() - start)
    getmask = GetMask(frame)
    processed = decision(getmask)
    if processed is None:
        break
        
    out.write(processed)

    #count += 1
out.release()
cap.stop()

