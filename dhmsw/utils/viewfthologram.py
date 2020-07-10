import numpy as np
import matplotlib.pyplot as plt
import time
import sys
from skimage.io import imsave
from pymba import *
from shampoo_lite.reconstruction import Hologram
sys.path.append('..')
import DEFAULT

with Vimba() as vimba:
    system = vimba.getSystem()

    #system.runFeatureCommand("GeVDiscoveryAllOnce")
    time.sleep(0.2)

    camera_ids = vimba.getCameraIds()

    for cam_id in camera_ids:
        print("Camera found: ", cam_id)

    c0 = vimba.getCamera(camera_ids[0])
    c0.openCamera()


    #c0.Width = 2048
    #c0.Height = 2048

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
    img = None
    if success:
        img = np.ndarray(buffer=frame_data,
                         dtype=np.uint8,
                         shape=(frame.height,frame.width,1))
        #imsave('snapimg.tiff', img)

    c0.endCapture()
    c0.revokeAllFrames()
    c0.closeCamera()

    holo = Hologram(img[:,:,0], wavelength=DEFAULT.wavelength)

    ft_holo = holo.ft_hologram

    plt.figure()
    plt.imshow(np.log(np.abs(holo.ft_hologram)**2))
    #plt.show()
    plt.figure()
    for i in range(len(DEFAULT.wavelength)):
        plt.imshow(np.log(np.abs(holo.ft_hologram * DEFAULT.fourier_mask.mask[:,:,i])**2))
    plt.show()

