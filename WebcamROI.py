import numpy as np
import cv2
import imutils
import time

# multiple cascades: https://github.com/Itseez/opencv/tree/master/data/haarcascades

#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_eye.xml
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

cap = cv2.VideoCapture(0)
SEND_BOX = []

while 1:
    ret, raw = cap.read()
    raw = imutils.resize(raw, width = 500)

    ######################
    ####SEND
    ######################
    if SEND_BOX != []:
        [top, bot, lft, rgt] = list.copy(SEND_BOX)
        send = raw[top:bot, lft:rgt]
        top_offset = top
        lft_offset = lft
    else:
        send = raw.copy()
        top_offset = 0
        lft_offset = 0

    ######################
    ####CALC
    ######################
    img = send.copy()
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    index = 0
    currmax = 0
    i = 0

    START = time.time()
    
    for i in range (0, len(faces)):        
        (x,y,w,h) = faces[i]
        temp = w*h
        if w+h > currmax:
            currmax = w*h
            index = i

    if len(faces) != 0:
        (x,y,w,h) = faces[index]
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)

        #LATER
        #1. Display face on a white background, with SEND_BOX displayed yellow
        #2. Track history, average total movement of last five
        #       If overall moved left, extend left

        #PREDICTING BOX, bigger than face detect
        SEND_BOX = [top_offset+y - 20, top_offset+y+h + 20,
                    lft_offset+x - 20, lft_offset+x+w + 20]

        height, width, channels = raw.shape
        send_height, send_width, send_channels = send.shape
        blank_image = np.zeros((height,width,3), np.uint8)
        blank_image[top_offset:top_offset+send_height,
                    lft_offset:lft_offset+send_width] = img
        cv2.rectangle(blank_image,(SEND_BOX[2],SEND_BOX[0]),
                      (SEND_BOX[3],SEND_BOX[1]),(0,255,255),2)
        img=blank_image
        
    else:
        #NO FACE, SEND WHOLE IMAGE
        send_height, send_width, send_channels = send.shape
        cv2.rectangle(img,(0,0),
                      (send_width,send_height),(0,255,255),2)
        SEND_BOX = []

    END = time.time()
    seconds = END - START
    print("Time taken : {0} seconds".format(seconds))

    ######################
    ####DISPLAY
    ######################
    cv2.imshow('Raw',raw)
    
    try:
        cv2.imshow('Send',send)
    except:
        print("could not send")
        continue

    try:
        cv2.imshow('Calc',img)
    except:
        print("could not calc")
        continue
    
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()
