import numpy as np
import time
import sys
from skimage.io import imsave
from pymba import *


with Vimba() as vimba:
    system = vimba.getSystem()

    #system.runFeatureCommand("GeVDiscoveryAllOnce")
    time.sleep(0.2)

    camera_ids = vimba.getCameraIds()

    for cam_id in camera_ids:
        print("Camera found: ", cam_id)

    if not camera_ids:
        sys.exit('No cameras found.  Aborting.')

    c0 = vimba.getCamera(camera_ids[0])
    c0.openCamera()

    try:
        #gigE camera
        #print(c0.GevSCPSPacketSize)
        #print(c0.StreamBytesPerSecond)
        #c0.StreamBytesPerSecond = 100000000
        pass
    except:
        #set pixel format
        c0.PixelFormat="Mono8"
        #c0.ExposureTimeAbs=60000

    #c0.Width = 2048
    #c0.Height = 1944

    frame = c0.getFrame()
    frame.announceFrame()

    c0.startCapture()
    framecount = 0
    droppedframes = []
    lasttime = time.time()

    try:
        frame.queueFrameCapture()
        success = True
    except:
        droppedframes.append(framecount)
        success = False
    c0.runFeatureCommand("AcquisitionStart")
    c0.runFeatureCommand("AcquisitionStop")
    frame.waitFrameCapture(1000)
    frame_data = frame.getBufferByteData()
    if success:
        img = np.ndarray(buffer=frame_data,
                         dtype=np.uint8,
                         shape=(frame.height,frame.width,1))
        imsave('snapimg.tiff', img)

    c0.endCapture()
    c0.revokeAllFrames()
    c0.closeCamera()


