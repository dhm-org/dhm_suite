import sys, os
import functools
import signal
import select
import socket
import numpy as np
import pickle
import time
import platform

from io import BytesIO
from pylab import figure,axes,pie,title,show 
import time
from datetime import datetime
from multiprocessing import Process, Queue
import threading
import queue as queue
import interface
import struct
from PIL import Image 

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtQuick import *
from PyQt5.QtQml import *

#GLOBALS
# Struct is from dhm_streaming/include/CamFrame.h
# Q = unsinged long long int
# I = unsigned Int
headerStruct = struct.Struct('QQQQQQQdddddddd')


class guiclient(QThread):
    sig_img = pyqtSignal(int,str, np.ndarray)
    sig_hist_val = pyqtSignal(int,int)
    sig_header = pyqtSignal(int, int, int, object, int, int, int, int, int, int,float,float) #header: height, width, frameID, timestamp, gain min, gain max, exposure min, exposure max, gain, exposure, m_rate, m_rate_measured
    sig_img_complete = pyqtSignal(str)
    def __init__(self,server,port):
        QThread.__init__(self)
        super().__init__()

        self.sock = None 
        self.exit = False
        self.maxlen = 150995023
        self.histogram =0
        self.bins = 0
        self.clientMontiorThread = None
        self.server = server
        self.port = port
        self.performance_val = 1
        self.quit = False
        self.outdata = None
        self.init = False
        self.outdata_RGB = None
        self.enable_image = True
        self.enable_histogram = True

        self.w = None 
        self.h = None
        self.msg = None
        self.offset = None
        self.dtype = None

        # from CamFrame struct
        self.m_width = None
        self.m_height = None
        self.m_img_size = None 
        self.m_databuffersize = None 
        self.m_timestamp = None 
        self.m_frame_id = None 
        self.m_data = None
        self.m_logging = None
        self.m_gain = None
        self.m_gain_min = None
        self.m_gain_max = None
        self.m_exposure = None
        self.m_exposure_min = None
        self.m_exposure_max = None
        self.m_rate = None
        self.m_rate_measured = None

        if platform.system() == 'Linux':
            for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
                signal.signal(sig, self.signal_handler)



    def signal_handler(self, signal, frame):
        print("DHMx: Gui Thread exiting...")
        self.exit = True
        sys.exit()



    # This will launch and run the Display Thread as a Qt thread
    def unpack_message(self,msg):
            self.msg = msg
            self.dtype = np.uint8
            self.w = self.m_width
            self.h = self.m_height
            self.dimensions = self.m_width,self.m_height
            #self.offset = struct.calcsize(headerStruct.format) 
            self.offset = struct.calcsize(headerStruct.format)

            # Grab data from the DHM server...
            try:
               self.outdata = \
                  np.frombuffer\
                      (self.msg[self.offset:self.offset+self.m_img_size],\
                      dtype=self.dtype).reshape(self.dimensions)

            except Exception as e:
               print("Unable to receive full message from camera server: ",repr(e))
               return -1

            # make the array writable
            if platform.system() == 'Linux':
                self.outdata.setflags(write=1)

            if self.enable_histogram:
               # Bin historgram values together to display
               self.histogram,self.bins = np.histogram(self.outdata,bins=np.arange(0,256,1))
               for i in range(255):
                  self.sig_hist_val.emit(i,self.histogram[i])

            if self.enable_image:
               # Create an RGB version of the received image to display
               # absolute minimums and maximums
               self.outdata_RGB = np.stack((self.outdata,)*3, axis=-1)
               self.outdata_RGB[self.outdata == 255] = [255,0,0]
               self.outdata_RGB[self.outdata == 0] = [0,0,255]  

               # Create an image timestamp in UTC format
               current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

               # Emit to Qt/QML that the processed image is ready
               # to be displayed.
               # NOTE: Had to swap the signal for width and height
               # for QML (See dhmx for more details)
               self.sig_img_complete.emit(current_time)
               self.sig_header.emit(self.m_height, self.m_width, self.m_frame_id, self.m_timestamp, self.m_gain_min, self.m_gain_max, self.m_exposure_min, self.m_exposure_max, self.m_gain, self.m_exposure, self.m_rate, self.m_rate_measured)
               self.init = True



    # gets index 0-255 and returns a value associated with the luma range
    # of 0 (absolute black) to 255 (absolute white)
    def get_histogram_val(self, pos):
        return self.bins[pos]



    def shutdown(self):
        self.clientMontiorThread.join()
        self.clientMontiorThread.close()
        print("Done")
        self.terminate()
        

    def Connect(self):
       self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       connected = False
       while(connected != True):
          try:
              self.sock.connect((self.server, self.port))
              connected = True
          except:
              print("Could not connect to the the display server.  Trying again...")
              time.sleep(1)
       print("Connnected display server.")
       self.readfds = [self.sock]

    def run(self):
        connected = False
        ### Continous receive of data
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        length = None
        buf = b''
        data = b''
        msg=b''
        meta = None
        totalbytes = 0
        
        # Attempt connection
        self.Connect()


        while not self.quit:
            infds, outfds, errfds = select.select(self.readfds, [], [],1)

            if not (infds or outfds or errfds):
                continue
            if self.exit: break

            for s in infds:
                if s is self.sock:
                    #packet = self.sock.recv(150995023)
                    packet = self.sock.recv(65535)
                    if not packet:
                        self.Connect()
                        #self.exit = True
                        #break
                    data += packet
                    datalen = len(data)
                    
                    if meta is None and datalen > struct.calcsize(headerStruct.format):
                        try:
                           self.m_width, \
                           self.m_height, \
                           self.m_img_size, \
                           self.m_databuffersize, \
                           self.m_timestamp, \
                           self.m_frame_id, \
                           self.m_logging, \
                           self.m_gain,\
                           self.m_gain_min,\
                           self.m_gain_max,\
                           self.m_exposure,\
                           self.m_exposure_min,\
                           self.m_exposure_max,\
                           self.m_rate,\
                           self.m_rate_measured,\
                              = headerStruct.unpack(data[0:struct.calcsize(headerStruct.format)])
                           meta = (self.m_width)
                        except:
                           print("DHMx-c Diplsay: Did not receive proper header.  Header missing or incomplete.")
                           return -10
                        # frame data + header = full image message
                        totalbytes = self.m_databuffersize + struct.calcsize(headerStruct.format)
                        if datalen >= totalbytes: 
                            msg = data[:totalbytes]
                            data = data[totalbytes:]
                            
                            totalbytes = 0
                            self.unpack_message(msg)
                    else:
                        if datalen < totalbytes:
                            continue
                        msg = data[:totalbytes]
                        data = data[totalbytes:]
                        meta = None
                        totalbytes = 0
                        self.unpack_message(msg)


            if self.exit: break
        self.sock.close() 

