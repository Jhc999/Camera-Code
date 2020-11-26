import PySpin
import time 
import csv
import numpy as np
import cv2
import imutils

############################################################
with open('results.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile)
    spamwriter.writerow(["Pixel","FPS","CaptureTime"])

NUM_IMAGES = 50  # number of images to grab

############################################################

############################################################
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
SEND_BOX = []


############################################################

def configure_custom_image_settings(nodemap, OFFSETX, OFFSETY, SETWIDTH, SETHEIGHT):
    print("Params: ", OFFSETX, OFFSETY, SETWIDTH, SETHEIGHT)
    
    node_width = PySpin.CIntegerPtr(nodemap.GetNode("Width"))
    node_height = PySpin.CIntegerPtr(nodemap.GetNode("Height"))                      
    node_offset_x = PySpin.CIntegerPtr(nodemap.GetNode("OffsetX"))       
    node_offset_y = PySpin.CIntegerPtr(nodemap.GetNode("OffsetY"))              
    
    node_offset_x.SetValue(0)
    node_offset_y.SetValue(0)

    node_width.SetValue(SETWIDTH)
    node_height.SetValue(SETHEIGHT)
    node_offset_x.SetValue(OFFSETX)
    node_offset_y.SetValue(OFFSETY)

    return True

############################################################
if __name__ == "__main__":
    #[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, float('inf')]

    system = PySpin.System.GetInstance()
    cam_list = system.GetCameras()
    cam = cam_list.GetByIndex(0)
    OFFSETX = 2000
    OFFSETY = 2000
    SETWIDTH = 1000 #5320
    SETHEIGHT = 1000 #4600
    LENGTH= 0.5 #float("inf")#0.05
    

#-----------------------------------------------------------
    
    start = time.time()

    cam.Init()
    count = 0
    resizeW = 400
    
    
    while count < NUM_IMAGES:

        ####$$$$$$$$$$$$$
        
        FLAG1 = time.time()
        cam_to_pc=[OFFSETX,OFFSETY]
        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap() #can be moved outside, time is 1.6e-05
        configure_custom_image_settings(nodemap, OFFSETX, OFFSETY, SETWIDTH, SETHEIGHT)
        STARTING = time.time()
        CURRENT = 0
        node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode("AcquisitionMode"))
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName("Continuous")
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)
        FLAG7 = time.time()
        cam.BeginAcquisition()
        FLAG8 = time.time()
        print("BEGIN", FLAG8-FLAG7)
        print("TOTAL", FLAG8-FLAG1) 
        
        # BOTTLENECK TIMINGS
        # CAM.BeginAcquisition() 0.175
        # configure_custom_image_settings() 0.03

        #image_result = cam.GetNextImage()
        #image_converted = image_result.Convert(PySpin.PixelFormat_BGR8, PySpin.HQ_LINEAR)
        #frame = image_converted.GetData().reshape(SETHEIGHT,SETWIDTH,3)

        #starting = time.time()  #theoretical maximum timing started here

        while CURRENT - STARTING < LENGTH:
            CURRENT = time.time()
            thetime = CURRENT - STARTING
            print("IMAGE: "+str(count))
            image_result = cam.GetNextImage()

            #image_converted = image_result.Convert(PySpin.PixelFormat_BGR8, PySpin.HQ_LINEAR)
            #frame = image_converted.GetData().reshape(SETHEIGHT,SETWIDTH,3)
            #image_converted.Save(str(count)+".jpg")
            #image_converted.Save("test.jpg")
            #frame=cv2.imread('test.jpg')

            #row_bytes = float(len(image_converted.GetData()))/float(image_converted.GetWidth())
            #rawFrame = np.array(image_converted.GetData(), dtype="uint8").reshape( (image_converted.GetHeight(), image_converted.GetWidth()) )
            #frame = cv2.cvtColor(rawFrame, cv2.COLOR_BGR2RGB)

            #frame = imutils.resize(frame, width=resizeW)
            #cv2.imshow('',frame)
            #cv2.waitKey(1)
            #image_result.Release()
                
            count += 1
            if count >= NUM_IMAGES:
                break

            ######################################################################
            ######################################################################
            ######################################################################
        #cam.EndAcquisition()
        #break
        '''
        img = imutils.resize(frame, width=resizeW)
        cv2.imshow('',img)
        cv2.waitKey(1)
            
        ######
        #CALC#
        ######
        # img = frame.copy()
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        index = 0
        currmax = 0
        i = 0
        for i in range (0, len(faces)):        
            (x,y,w,h) = faces[i]
            temp = w*h
            if w+h > currmax:
                currmax = w*h
                index = i

        if len(faces) != 0:
            (x,y,w,h) = faces[index]
            #cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            #PREDICTING BOX, bigger than face detect
            lft_offset=cam_to_pc[0]
            top_offset=cam_to_pc[1]
            x,y,w,h = int(x*SETWIDTH/resizeW), int(y*SETWIDTH/resizeW), int(w*SETWIDTH/resizeW), int(h*SETWIDTH/resizeW)
            SEND_BOX = [top_offset+y - 200, top_offset+y+h + 200,
                        lft_offset+x - 200, lft_offset+x+w + 200]
            
        else:
            #NO FACE, SEND WHOLE IMAGE
            SEND_BOX = []

        ######
        #SEND#
        ######
        if SEND_BOX != []:
            [top, bot, lft, rgt] = list.copy(SEND_BOX)
            #send = raw[top:bot, lft:rgt]
            OFFSETY = top - (top%4)
            OFFSETX = lft - (lft%4)
            SETWIDTH = (rgt-lft) - (rgt-lft)%4
            SETHEIGHT = (bot-top) - (bot-top)%4 

            if OFFSETX + SETWIDTH>5320:
                diffW=OFFSETX+SETWIDTH-5320
                SETWIDTH-=diffW
            if OFFSETY + SETHEIGHT>4600:
                diffH=OFFSETY+SETHEIGHT-4600
                SETHEIGHT-=diffH

        else:
            OFFSETY = 0
            OFFSETX = 0
            SETWIDTH = 5320
            SETHEIGHT = 4600
            
            ######################################################################
            ######################################################################
            ######################################################################
        '''
        image_result.Release()
        cam.EndAcquisition() 

    # Deinitialize camera
    #cam.DeInit()

    end = time.time()
    seconds = end - start
    FPS = count/seconds
    print("FPS: "+str(FPS))
    print("Frames: "+str(count))
    print("Seconds: "+str(seconds))
    
#-----------------------------------------------------------
    
    del cam
    cam_list.Clear()
    system.ReleaseInstance()
############################################################
