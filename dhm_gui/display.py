import sys, os
import functools
import signal
import select
import socket
import numpy as np # CAUTION: Please use numpy version 1.15.4
import pickle
import time

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
headerStruct = struct.Struct('III')
MAX_BUFFER = 3 #since we are reading in image files, create a ring buffer and overwrite

class guiclient(QThread):
    sig_img = pyqtSignal(int,str, np.ndarray)
    sig_hist_val = pyqtSignal(int,int)
    sig_img_complete = pyqtSignal(str)
    def __init__(self,server,port):
        QThread.__init__(self)
        super().__init__()
        print(server, port)
        self.sock = None 
        self.win_mode = "" #to be used to determine what type of window, e.g. fourier, amplitude, phase, etc. 
        self.exit = False
        self.maxlen = 150995023
        self.counter = 0
        self.histogram =0
        self.bins = 0
        self.clientMontiorThread = None
        self.server = server
        self.port = port
        self.reconst = False
        self.wavelength = 0
        self.prop_distance = 0
        self.performance_val = 1
        self.quit = False
        self.outdata = None
        self.init = False
        self.outdata_RGB = None
        self.enable_histogram = False

        self.z = np.zeros((2448,2050),dtype=np.uint8)
        self.w = None 
        self.h = None
        self.l = None
        self.msgid = None 
        self.srcid = None 
        self.totalbytes = None
        self.msg = None
        self.meta = None
        self.offset = None

        self.ndim_struct = None
        self.ndimsize = None
        self.ndim = None

        self.dimStruct = None
        self.dimsize = None
        self.dimensions = None

        self.dtype = None

        print("*** DISPLAY WINDOW CREATED ***")

        for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
            signal.signal(sig, self.signal_handler)


    def set_mode(self,mode):
        if(mode == "reconst"):
           self.reconst = True
        else:
           self.reconst = False

    def signal_handler(self, signal, frame):
        print("DHMx: Gui Thread exiting...")
        self.exit = True
        sys.exit()


    def restore_frame(self, data, meta, z):
        w, h, compval, val, size, actualsize,ts, gain, ccdtemp = meta
        
        dtidx = 0
        for i in range(0, w*h,compval):
            z[i] = data[dtidx];
            dtidx += 1
        

    def get_pixel_val(self,x,y):
       # Check if the image sending has been initialized by its first frame to sample
       if(self.init != False ):
          # Check to make sure the mouse is within bounds.  Some images may not be exactly 2048x2048
          if((np.size(self.outdata,0) >= x and np.size(self.outdata,1) >= y)):
             if(self.reconst and self.win_mode != 'fourier'):
                return int(self.outdata[x-1,y-1,self.prop_distance,self.wavelength])
             else:
                return int(self.outdata[x-1,y-1])
       else:
          return 0






    # This will launch and run the Display Thread as a Qt thread
    def unpack_message(self,msg):
            self.msg = msg
            try:
               self.msgid, self.srcid, self.totalbytes = headerStruct.unpack(self.msg[0:struct.calcsize(headerStruct.format)])
            except:
               print("DHMx Diplsay: Did not receive proper header.  Header missing or incomplete.")
               return -10
            self.meta = (self.msgid, self.srcid, self.totalbytes)
            self.offset = struct.calcsize(headerStruct.format) 
            
            self.ndim_struct = struct.Struct('H')
            self.ndimsize = struct.calcsize(self.ndim_struct.format)
            self.ndim = self.ndim_struct.unpack(self.msg[self.offset:self.offset + self.ndimsize])[0]

            self.dimStruct = struct.Struct('H'*int(self.ndim))
            self.dimsize = struct.calcsize(self.dimStruct.format)
            self.dimensions = self.dimStruct.unpack(self.msg[self.offset + self.ndimsize:self.offset + self.ndimsize + self.dimsize])

            self.offset = self.offset + self.ndimsize + self.dimsize

            if self.srcid == interface.SRCID_IMAGE_FOURIER:
                self.dtype = np.uint8
                self.w, self.h = self.dimensions
            elif self.srcid == interface.SRCID_IMAGE_RAW:
                self.dtype = np.uint8
                self.w, self.h = self.dimensions
            else:
                self.dtype = np.uint8
                self.w, self.h, self.z, self.l = self.dimensions



            if(self.srcid == interface.SRCID_IMAGE_AMPLITUDE and self.win_mode == "amplitude") or\
              (self.srcid == interface.SRCID_IMAGE_PHASE and self.win_mode == "phase") or\
              (self.srcid == interface.SRCID_IMAGE_FOURIER and self.win_mode == "fourier") or\
              (self.srcid == interface.SRCID_IMAGE_RAW and self.win_mode == "raw") or\
              (self.srcid == interface.SRCID_IMAGE_INTENSITY and self.win_mode == "intensity"):

                 # Grab data from the DHM server...
                 self.outdata = np.frombuffer(self.msg[self.offset:self.offset+(functools.reduce(lambda x,y: x*y, self.dimensions)*np.dtype(self.dtype).itemsize)], dtype=self.dtype).reshape(self.dimensions)

                 # make the array writable
                 self.outdata.setflags(write=1)

                 #rescaled for performance increase of upwards of 40+%
                 self.outdata = self.outdata[::self.performance_val, ::self.performance_val]

                 # Rescale image
                 if(self.outdata.max() != 0): 
                    self.outdata *= int(255.0/self.outdata.max())

                 # If the user selects the histogram button and enables the histogram, compute the bins necessary to display
                 # NOTE: Histogram computations in real time are CPU costly, so it is best to only ue this if/when needed.
                 if(self.enable_histogram):
                    # calculate the histogram on the grayscale 'outdata' object from 0-255
                    # Emit the position of the histogram back to Qt/QML to update the histogram
                    if(self.reconst and self.win_mode != 'fourier'):
                       self.histogram,self.bins = np.histogram(self.outdata[:,:,self.prop_distance,self.wavelength],bins=np.arange(0,256,1))
                    else:
                       self.histogram,self.bins = np.histogram(self.outdata,bins=np.arange(0,256,1))
                    for i in range(255):
                       self.sig_hist_val.emit(i,self.histogram[i])

                 # Create an RGB version of the received image to display absolute minimums and maximums
                 if(self.reconst and self.win_mode != 'fourier'):
                    self.outdata_RGB = np.stack((self.outdata[:,:,self.prop_distance,self.wavelength],)*3, axis=-1)
                    self.outdata_RGB[self.outdata[:,:,self.prop_distance,self.wavelength] == 255] = [255,0,0]
                    self.outdata_RGB[self.outdata[:,:,self.prop_distance,self.wavelength] == 0] = [0,0,255] 
                 else:
                    self.outdata_RGB = np.stack((self.outdata,)*3, axis=-1)
                    self.outdata_RGB[self.outdata == 255] = [255,0,0]
                    self.outdata_RGB[self.outdata == 0] = [0,0,255]  

                 # Create an image timestamp in UTC format
                 current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

                 # Emit to Qt/QML that the processed image is ready to be displayed
                 self.sig_img_complete.emit(current_time)
                 self.init = True



    def set_win(self,mode):
        self.win_mode = mode



    # gets index 0-255 and returns a value associated with the luma range
    # of 0 (absolute black) to 255 (absolute white)
    def get_histogram_val(self, pos):
        return self.bins[pos]



    def shutdown(self):
        self.clientMontiorThread.join()
        self.clientMontiorThread.close()
        print("Done")
        self.terminate()
        

    def recvall(self,sock,n):
       data = b''
       while len(data) < n:
          packet = sock.recv(n - len(data))
          if not packet:
             return None
          data += packet
       return data

    def run(self):
        ### Continous receive of data
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server, self.port))
        self.readfds = [self.sock]

        ### Start Display Thread
        #self.displaythread.start()
        length = None
        buf = b''
        data = b''
        msg=b''
        meta = None
        totalbytes = 0
        
        while not self.quit:
            infds, outfds, errfds = select.select(self.readfds, [], [])

            if not (infds or outfds or errfds):
                continue
            if self.exit: break

            for s in infds:
                if s is self.sock:
                    ### Get as much data as we can
                    #packet = self.sock.recv(150995023)

                    # The data size is 2048x2048 * 3
                    packet = self.sock.recv(12582912)
                    if not packet:
                        self.exit = True
                        self.displayQ.put_nowait(None)
                        break
                    data += packet
                    datalen = len(data)
                    if meta is None and datalen > struct.calcsize(headerStruct.format):
                        try:
                            msg_id, srcid, totalbytes = headerStruct.unpack(data[0:struct.calcsize(headerStruct.format)])
                        except:
                            print("DHMx Diplsay: Did not receive proper header.  Header missing or incomplete.")
                            return -10
                        totalbytes += struct.calcsize(headerStruct.format)
                        self.meta = (msg_id, srcid)
                        if datalen >= totalbytes: 
                            msg = data[:totalbytes]
                            data = data[totalbytes:]
                            meta = None
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

