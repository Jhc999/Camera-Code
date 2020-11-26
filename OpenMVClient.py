import sensor, time, image,pyb, sys, utime
import network, usocket

########################################################################
def MVread(str_in):     #READ CONFIG MESSAGE SENT BY PC
    offX = ''
    offY = ''
    width = ''
    height = ''
    commaNum = 0
    for j in range (0, len(str_in)):
        if str_in[j] == ',':
            commaNum += 1
        else:
            if commaNum == 0:
                offX += (str_in[j])
            if commaNum == 1:
                offY += (str_in[j])
            if commaNum == 2:
                width += (str_in[j])
            if commaNum == 3:
                height += (str_in[j])
            if commaNum == 4:
                break
    #print(str_in)
    #print(int(offX), int(offY), int(width), int(height))
    return int(offX), int(offY), int(width), int(height)

def jpegDim(x,y,w,h):
    #assuming w < 200
    #assuming h < 200
    diffW = int((200-w)/2)
    diffH = int((200-h)/2)
    return (x - diffW), (y - diffH)


########################################################################

sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.HD)   # Set frame size to WQXGA2 (2592x1944) or QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.

SSID ='TELUS3061'     # Network SSID
KEY  ='m2gbx75frq'     # Network key


wlan = network.WINC()
wlan.connect(SSID, key=KEY, security=wlan.WPA_PSK)
print(wlan.ifconfig())

HOST = '192.168.1.64'  # The server's hostname or IP address
PORT = 3304       # The port used by the server

s = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
s.connect((HOST, PORT))
s.settimeout(2.0)   #0 is non-blocking, None is blocking

data = s.recv(18)
print("WAIT",data)
data = s.recv(18)
print("WAIT",data)


numFRAMES = 25
lenBOUND = 50000       # Above bound is compressed JPEG, below bound is full RGB

########################################################################

def main():
    ## SEN LEN AND OFFSETS, RECEIVE CONFIRMATION

    x = 0
    y = 0
    w = 1280
    h = 720
    boundW = 250
    boundH = 250

    currw = 1280
    lastw = 1280
    lasth = 720

    for i in range (0, numFRAMES):
        #print("FRAMENUM", i)
        #print("\n")

        ################################################################################
        TIME1 = utime.ticks_ms()

        #if currw == 1280:
            #sensor.set_windowing((x,y,w,h))
        #else:
            #setX, setY = jpegDim(x,y,w,h)
            #sensor.set_windowing((setX, setY, 200, 200))  #Calculate tracking window
            #print("settings", setX, setY)
        sensor.set_windowing((x,y,w,h))
        TIME2 = utime.ticks_ms()

        if currw != lastw:
            sensor.skip_frames(time=50) #If w and h change need time to set

        TIME3 = utime.ticks_ms()

        if currw == 1280:
            frame = sensor.snapshot() #.crop((x,y,w,h))
            data = frame.compress(40).bytearray()
            len1 = len(data)   #1st image is full jpeg
            len2 = 0            #2nd image none
            TIME4 = utime.ticks_ms()
            TIME5 = utime.ticks_ms()
            TIME51 = utime.ticks_ms()
        else:
            frame = sensor.snapshot()
            TIME4 = utime.ticks_ms()
            #data = frame.copy((int(x-setX),int(y-setY),w,h)).bytearray()
            data = frame.copy((75,63,100,60)).bytearray()
            TIME5 = utime.ticks_ms()
            frame = frame.compress(40).bytearray()
            TIME51 = utime.ticks_ms()

            len1 = len(frame)    #1st image is tracking jpeg
            len2 = len(data)       #2nd image is RGB data
            #print("LENGTH CHECK", len1, len2)
            data = frame+data
        lastw = currw
        ################################################################################




        config = str(len1)+','+str(len2)+','
        config = config.encode()

        dummyvar = bytearray(16 - len(config)) #Server expecting a 16 bytes message
        config += dummyvar

        TIME52 = utime.ticks_ms()
        s.send(config)
        TIME53 = utime.ticks_ms()

        ### SEN IMG, RECEIVE OFFSETS AND DIMENSIONS
        totalsend = 0
        TIME6 = utime.ticks_ms()
        s.write(data)
        #imLen = len1+len2
        #while totalsend < imLen:
        #    sent = s.send(data[totalsend:min(imLen,totalsend+200000)])
        #    totalsend += sent
        #    print(totalsend)
        #print(i, len(data))
        TIME7 = utime.ticks_ms()
        data = s.recv(18)
        TIME8 = utime.ticks_ms()
        x, y, w, h = MVread(data.decode())

        #if i%5 == 0:
        #    x,y,w,h = 0,0,1280,720
        #else:
        #    x,y,w,h = 100,100,200,200

        if w == 1280:
            currw = 1280
        else:
            currw = 200

        #print(i,x,y,w,h)
        #print('Received2', offx, offy, width, height)
        TIME9 = utime.ticks_ms()

        print("Seg1", (TIME2-TIME1)/1000)
        print("Seg2", (TIME3-TIME2)/1000)
        print("Seg3", (TIME4-TIME3)/1000)
        print("Seg4", (TIME5-TIME4)/1000)
        print("Seg5", (TIME51-TIME5)/1000)
        print("Seg51", (TIME52-TIME51)/1000)
        print("Seg52", (TIME53-TIME52)/1000)
        print("Seg53", (TIME6-TIME53)/1000)
        print("Seg6", (TIME7-TIME6)/1000)
        print("Seg7", (TIME8-TIME7)/1000) #0.04!!!!!!
        print("Seg8", (TIME9-TIME8)/1000) #0.04!!!!!!
        print("FRAME", (TIME9-TIME1)/1000)

BIGSTART = utime.ticks_ms()
main()
BIGEND = utime.ticks_ms()
s.close()
print("FPS")
print(numFRAMES/((BIGEND-BIGSTART)/1000))


#OpenMV is sending relly fast, PC is receiving really slow
#PC can only decode if sensor.JPEG or sensor.RGB565.compress()... which is just JPEG

# ustructs and uctypes? faster data send?
