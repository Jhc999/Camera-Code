import PySpin
import time 
import csv

'''
  X  |  Y  | Line
Pixel| FPS | time
 
'''

with open('resultsBLACK.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile)
    spamwriter.writerow(["Pixel","FPS","CaptureTime"])

NUM_IMAGES = 50  # number of images to grab

def configure_custom_image_settings(nodemap, mode,
                                    mode0_OFFSETX, mode0_OFFSETY, mode0_SETWIDTH, mode0_SETHEIGHT,
                                    mode1_OFFSETX, mode1_OFFSETY, mode1_SETWIDTH, mode1_SETHEIGHT):
    """
    Configures a number of settings on the camera including offsets  X and Y, width,
    height, and pixel format. These settings must be applied before BeginAcquisition()
    is called; otherwise, they will be read only. Also, it is important to note that
    settings are applied immediately. This means if you plan to reduce the width and
    move the x offset accordingly, you need to apply such changes in the appropriate order.

    :param nodemap: GenICam nodemap.
    :type nodemap: INodeMap
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    #mode == 1, 1x1
    SETWIDTH = mode1_SETWIDTH
    SETHEIGHT = mode1_SETHEIGHT
    OFFSETX = mode1_OFFSETX
    OFFSETY = mode1_OFFSETY
    
    if mode == 0:
        SETWIDTH = mode0_SETWIDTH
        SETHEIGHT = mode0_SETHEIGHT
        OFFSETX = mode0_OFFSETX
        OFFSETY = mode0_OFFSETY
    
    node_width = PySpin.CIntegerPtr(nodemap.GetNode("Width"))
    node_width.SetValue(SETWIDTH)

    node_height = PySpin.CIntegerPtr(nodemap.GetNode("Height"))                      
    node_height.SetValue(SETHEIGHT)

    node_offset_x = PySpin.CIntegerPtr(nodemap.GetNode("OffsetX"))       
    node_offset_x.SetValue(OFFSETX)

    node_offset_y = PySpin.CIntegerPtr(nodemap.GetNode("OffsetY"))              
    node_offset_y.SetValue(OFFSETY)

    return True


def print_device_info(nodemap):
    """
    This function prints the device information of the camera from the transport
    layer; please see NodeMapInfo example for more in-depth comments on printing
    device information from the nodemap.

    :param nodemap: Transport layer device nodemap.
    :type nodemap: INodeMap
    :returns: True if successful, False otherwise.
    :rtype: bool
    """

    print("*** DEVICE INFORMATION ***\n")

    try:
        result = True
        node_device_information = PySpin.CCategoryPtr(nodemap.GetNode("DeviceInformation"))

        if PySpin.IsAvailable(node_device_information) and PySpin.IsReadable(node_device_information):
            features = node_device_information.GetFeatures()
            for feature in features:
                node_feature = PySpin.CValuePtr(feature)
                print("%s: %s" % (node_feature.GetName(),
                                  node_feature.ToString() if PySpin.IsReadable(node_feature) else "Node not readable"))

        else:
            print("Device control information not available.")

    except PySpin.SpinnakerException as ex:
        print("Error: %s" % ex)
        return False

    return result


def acquire_images(cam, nodemap, nodemap_tldevice):

    node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode("AcquisitionMode"))
    node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName("SingleFrame")
    acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
    node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

    cam.BeginAcquisition()
    image_result = cam.GetNextImage()
    #image_converted = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)
    #image_converted.Save("Test.jpg")
    image_result.Release()
    cam.EndAcquisition() 

    return True


def run_single_camera(cam, LENGTH,
                      mode0_OFFSETX, mode0_OFFSETY, mode0_SETWIDTH, mode0_SETHEIGHT,
                      mode1_OFFSETX, mode1_OFFSETY, mode1_SETWIDTH, mode1_SETHEIGHT):
    """
    This function acts as the body of the example; please see NodeMapInfo example
    for more in-depth comments on setting up cameras.

    :param cam: Camera to run on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Retrieve TL device nodemap and print device information
        nodemap_tldevice = cam.GetTLDeviceNodeMap()

        result &= print_device_info(nodemap_tldevice)

        # Initialize camera
        cam.Init()

        #node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode("AcquisitionMode"))
        #node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName("SingleFrame")
        #acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
        #node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

        count = 0
        
        while count < NUM_IMAGES:
            # Retrieve GenICam nodemap
            nodemap = cam.GetNodeMap()
            configure_custom_image_settings(nodemap, count%2,
                                            mode0_OFFSETX, mode0_OFFSETY, mode0_SETWIDTH, mode0_SETHEIGHT,
                                            mode1_OFFSETX, mode1_OFFSETY, mode1_SETWIDTH, mode1_SETHEIGHT)
            
            STARTING = time.time()
            CURRENT = 0

            node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode("AcquisitionMode"))
            node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName("Continuous")
            acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
            node_acquisition_mode.SetIntValue(acquisition_mode_continuous)
            cam.BeginAcquisition()
            
            while CURRENT - STARTING < LENGTH:
                CURRENT = time.time()
                thetime = CURRENT - STARTING
                print("IMAGE: "+str(count))
                #result &= acquire_images(cam, nodemap, nodemap_tldevice)

                image_result = cam.GetNextImage()                
                #image_converted = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)
                #image_converted.Save(str(count)+".jpg")
                image_result.Release()
                    
                count += 1
                if count >= NUM_IMAGES:
                    break

            cam.EndAcquisition() 

            print("LENGTH: "+str(LENGTH))
    
        # Deinitialize camera
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print("Error: %s" % ex)
        result = False

    return result


def main(LENGTH, mode0_OFFSETX, mode0_OFFSETY, mode0_SETWIDTH, mode0_SETHEIGHT,mode1_OFFSETX, mode1_OFFSETY, mode1_SETWIDTH, mode1_SETHEIGHT):
    """
    Example entry point; please see Enumeration example for more in-depth
    comments on preparing and cleaning up the system.

    :return: True if successful, False otherwise.
    :rtype: bool
    """
    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()

    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()

    num_cameras = cam_list.GetSize()

    print("Number of cameras detected: %d" % num_cameras)

    # Finish if there are no cameras
    if num_cameras == 0:

        # Clear camera list before releasing system
        cam_list.Clear()

        # Release system
        system.ReleaseInstance()

        print("Not enough cameras!")
        return False

    # Run example on each camera
    for i in range(num_cameras):
        cam = cam_list.GetByIndex(i)

        print("Running example for camera %d..." % i)

        result = run_single_camera(cam, LENGTH, mode0_OFFSETX, mode0_OFFSETY, mode0_SETWIDTH, mode0_SETHEIGHT,mode1_OFFSETX, mode1_OFFSETY, mode1_SETWIDTH, mode1_SETHEIGHT)
        print("Camera %d example complete..." % i)

    # Release reference to camera
    # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
    # cleaned up when going out of scope.
    # The usage of del is preferred to assigning the variable to None.
    del cam

    # Clear camera list before releasing system
    cam_list.Clear()

    # Release instance
    system.ReleaseInstance()

    return result

if __name__ == "__main__":
    LENGTH = 1

    '''
    #mode = 1
    mode1_OFFSETX   = 2
    mode1_OFFSETY   = 2
    mode1_SETWIDTH  = 104
    mode1_SETHEIGHT = 100

    if mode == 0:
        mode0_SETWIDTH = 104
        mode0_SETHEIGHT = 100
        mode0_OFFSETX = 0
        mode0_OFFSETY = 0
    '''

    pixelsMODE0 = [[200,200,104,100],[200,200,200,200],[200,200,304,300],[200,200,400,400],[200,200,504,500],
                   [200,200,600,600],[200,200,704,700],[200,200,800,800],[200,200,904,900],[200,200,1000,1000],
                   [200,200,1104,1100],[200,200,1200,1200],[200,200,1304,1300],[200,200,1400,1400],[200,200,1504,1500],
                   [200,200,1600,1536],[200,200,1704,1536],[200,200,1800,1536],[200,200,1904,1536],[0,0,2048,1536]]
    
    pixelsMODE1 = [[0,0,104,100],[0,0,200,200],[0,0,304,300],[0,0,400,400],[0,0,504,500],
                   [0,0,600,600],[0,0,704,700],[0,0,800,800],[0,0,904,900],[0,0,1000,1000],
                   [0,0,1104,1100],[0,0,1200,1200],[0,0,1304,1300],[0,0,1400,1400],[0,0,1504,1500],
                   [0,0,1600,1536],[0,0,1704,1536],[0,0,1800,1536],[0,0,1904,1536],[0,0,2048,1536]]
    
    timeset = [0.01, 0.05, 0.1, 0.5, 1.0, 5.0, float('inf')]

    for i in range(0, len(timeset)):
        for j in range (0, len(pixelsMODE0)):
            
            LENGTH = timeset[i]
            mode0_OFFSETX   = pixelsMODE0[j][0]
            mode0_OFFSETY   = pixelsMODE0[j][1]
            mode0_SETWIDTH  = pixelsMODE0[j][2]
            mode0_SETHEIGHT = pixelsMODE0[j][3]
            
            mode1_OFFSETX   = pixelsMODE1[j][0]
            mode1_OFFSETY   = pixelsMODE1[j][1]
            mode1_SETWIDTH  = pixelsMODE1[j][2]
            mode1_SETHEIGHT = pixelsMODE1[j][3]
            
            
            start = time.time()
            main(LENGTH, mode0_OFFSETX, mode0_OFFSETY, mode0_SETWIDTH, mode0_SETHEIGHT,mode1_OFFSETX, mode1_OFFSETY, mode1_SETWIDTH, mode1_SETHEIGHT)
            end = time.time()
            seconds = end - start
            print("Time taken : {0} seconds".format(seconds))

            '''
            X  |  Y  | Lines
            Pixel| FPS | time        
            '''
            
            with open('resultsBLACK.csv', 'a',newline='') as csvfile:
                spamwriter = csv.writer(csvfile)
                spamwriter.writerow([mode0_SETWIDTH*mode0_SETHEIGHT, NUM_IMAGES/seconds, LENGTH])
