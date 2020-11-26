import socket
import os
import io
import cv2
import numpy as np
import time
import imutils
import PIL
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

#########################################################################
HOST = '192.168.1.64'  # Standard loopback interface address (localhost)
PORT = 3304             # Port to listen on (non-privileged ports are > 1023)

numFRAMES = 25
boundW = 250       # Above bound is compressed JPEG, below bound is full RGB
boundH = 250

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

width = 1280
height = 720
offx = 0
offy = 0

#########################################################################
def PCread(str_in):     #READ CONFIG MESSAGE SENT BY OPENMV
    len1 = ''
    len2 = ''
    commaNum = 0
    for i in range (0, len(str_in)):
        if str_in[i] == ',':
            commaNum += 1
        else:
            if commaNum == 0:
                len1 += (str_in[i])
            if commaNum == 1:
                len2 += (str_in[i])
            if commaNum == 2:
                break
    return int(len1), int(len2)

def decodeRGB(bcolor, height, width):
    #print(bcolor[0:20])
    #print(bcolor[len(bcolor)-20:len(bcolor)])
    flag1 = time.time()
    MASK5 = 0b011111
    MASK6 = 0b111111
    im = np.empty([height,width], dtype=np.uint16)

    i = 0
    #flag2 = time.time()
    for y in range (0, height):
        for x in range (0, width):
            im[y,x] = int.from_bytes(bcolor[i+1:i+2]+bcolor[i:i+1], "little")
            i += 2
    #flag3 = time.time()
    b = (im & MASK5) << 3
    g = ((im >> 5) & MASK6) << 2
    r = ((im >> (5 + 6)) & MASK5) << 3
    bgr = np.dstack((b,g,r)).astype(np.uint8)
    #cv2.imshow("",bgr)
    #cv2.waitKey(0)
    flag4 = time.time()
    print("DECODE", flag4-flag1)
    return bgr

#########################################################################

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)

        msg1 = '1234567890abcdzzzz'
        msg2 = '1234567890abcdjjjj'
        msg1 = msg1.encode()
        msg2 = msg2.encode()
        conn.send(msg1)
        cv2.waitKey(1)
        conn.send(msg2)
        cv2.waitKey(1)

        BIGSTART = time.time()
        for i in range(0, numFRAMES):
            flag1 = time.time()

            #########################################################
            while True: #RECEIVE SETTINGS
                
                data1 = conn.recv(16) #####NEED TO PRESET THE LENGTH
                #print(data1)   
                #if not data1:
                #    break
                jpegLen, rgbLen = PCread(data1.decode())
                break
            imLen = jpegLen + rgbLen

            flag2 = time.time()
            #########################################################
            img = b''   #RECEIVE IMG
            msglen = 0
            while True:
                #print("HERE")
                flagA = time.time()
                data = conn.recv(imLen-msglen)
                #print("LENGTH", len(data))

                #if not data:
                #    break
                #########################################################
                if msglen < imLen:  #STILL RECEIVING
                    msglen += len(data)       
                    img += data
                flagB = time.time()
                #########################################################
                if msglen >= imLen: #DONE RECEIVING
                    STARTt = time.time()
                    #########################################################
                    if width > boundW:        #COMPRESSED jpeg
                        image = Image.open(io.BytesIO(img))
                        rgb_im = image.convert('RGB')
                        opencv_img = np.array(rgb_im)
                        opencv_img = opencv_img[:, :, ::-1].copy() 
                        #cv2.imshow("",opencv_img)
                        #cv2.waitKey(1)
                    #########################################################
                    if width <= boundW:       #FULL RGB
                        aaa = time.time()
                        jpegIMG = img[0:jpegLen] 
                        bbb = time.time()
                        rgbIMG = img[jpegLen:]
                        ccc = time.time()
                        image = Image.open(io.BytesIO(jpegIMG))
                        ddd = time.time()
                        rgb_im = image.convert('RGB')
                        eee = time.time()
                        opencv_img = np.array(rgb_im)
                        fff = time.time()
                        opencv_img = opencv_img[:, :, ::-1].copy() 
                        ggg = time.time()

                        print("a", bbb-aaa)
                        print("b", ccc-bbb)
                        print("c", ddd-ccc)
                        print("d", eee-ddd)
                        print("e", fff-eee)
                        print("f", ggg-fff)

                        rgb_data_img = decodeRGB(rgbIMG, 60, 100) #height, width)
                        #cv2.imwrite(str(i)+'.jpg', rgb_data_img)
                    #########################################################
                    ENDt = time.time()
                    print("INSIDE time", ENDt-STARTt)
                    break
                print("BA", flagB-flagA)
                #########################################################

            flag3 = time.time()

            imgcopy = opencv_img.copy()
            raw = imutils.resize(imgcopy, width = 500)
            gray = cv2.cvtColor(raw, cv2.COLOR_BGR2GRAY)

            flag4 = time.time()
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            index = 0
            currmax = 0
            
            flag5 = time.time()

            for j in range (0, len(faces)):        
                (xx,yy,ww,hh) = faces[j]
                temp = ww*hh
                if ww+hh > currmax:
                    currmax = ww*hh
                    index = j

            #print(i)
            if len(faces) != 0:
                prevW = width
                prevH = height
                scale = prevW/500   
                (newoffx,newoffy,width,height) = faces[index]
                
                #cv2.imwrite(str(i)+'.jpg', raw[newoffy:newoffy+height, newoffx:newoffx+width])

                #newoffx = int(newoffx*scale)
                #newoffy = int(newoffy*scale)
                #offx = max(0, (offx + newoffx - 15))
                #offy = max(0, (offy + newoffy - 15))
                #width = min(1280, int(width*scale + 30))
                #height = min(720, int(height*scale + 30))
                
                #cv2.imwrite(str(i)+'.jpg', opencv_img[offy:offy+height, offx:offx+width])
                #print(x,y,w,h)
                offx = offx + int(newoffx*scale)
                offy = offy + int(newoffy*scale)
                www = width*scale
                hhh = height*scale
                diffW = int((250-www)/2)
                diffH = int((250-hhh)/2)

                offx = offx - diffW
                offy = offy - diffH 
                height = 250
                width = 250
                

            if len(faces) == 0:
                offx = 0
                offy = 0
                width = 1280
                height = 720

            #offx, offy, width, height = int(offx), int(offy), int(width), int(height)

            flag6 = time.time()

            config = str(offx)+','+str(offy)+','+str(width)+','+str(height)+',' #'1000,100,100,100,'
            config = config.encode()
            dummyvar = bytearray(18-len(config)) #Client expecting a 18 bytes message
            config += dummyvar
            conn.send(config)

            flag7 = time.time()

            print("1", flag2-flag1)
            print("2", flag3-flag2)
            print("3", flag4-flag3)
            print("4", flag5-flag4)
            print("5", flag6-flag5)
            print("6", flag7-flag6)

            #print(config)

            #cv2.imshow("",opencv_img)
            #cv2.waitKey(1) 
            #cv2.imwrite(str(i)+'.jpg', rgb_data_img)

        BIGEND = time.time()
        #########################################################

print("FPS", numFRAMES/(BIGEND-BIGSTART))
conn.close()
