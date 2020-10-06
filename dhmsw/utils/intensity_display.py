import sys
import functools
import signal
import select
import socket
import numpy as np
import pickle
import matplotlib.pyplot as plt
import time
from multiprocessing import Process, Queue
sys.path.append('../dhmsw/')
import interface
import struct
PLOT = True

headerStruct = struct.Struct('III')

class guiclient(object):
    def __init__(self):
        self.sock = None
        self.displaythread = Process(target=self.DisplayThread)
        self.displaythread.daemon = True
        self.displayQ = Queue()
        self.exit = False

        self.maxlen = 150995023

        for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
            signal.signal(sig, self.signal_handler)

    def signal_handler(self, signal, frame):
        self.exit = True
        self.displayQ.put(None)
        
        
    def restore_frame(self, data, meta, z):
        w, h, compval, val, size, actualsize,ts, gain, ccdtemp = meta
        
        dtidx = 0
        for i in range(0, w*h,compval):
            z[i] = data[dtidx];
            dtidx += 1
        


    def DisplayThread(self):


        z = np.zeros((2448,2050),dtype=np.uint8)

        mydata2 = np.ones(2448*2050, dtype=np.uint8) * 255

        f = None
        axes = None
        if PLOT:
            f, axes = plt.subplots(sharex=True)
            for i in range(1):
                #axes[i].imshow(z, extent=[0,2448,0,2050], aspect="auto", cmap='gray')
                axes.clear()
                #axes.imshow(z, extent=[0,2448,0,2050], aspect="auto", cmap='gray')
        while True:
            msg = self.displayQ.get()
            if msg is None:
                break

            print("**************** Display Thread")   
            msgid, srcid, totalbytes= headerStruct.unpack(msg[0:struct.calcsize(headerStruct.format)])
            meta = (msgid, srcid, totalbytes)
            offset = struct.calcsize(headerStruct.format) 

            num_images = 1
            if srcid == interface.SRCID_IMAGE_AMPLITUDE_AND_PHASE or srcid == interface.SRCID_IMAGE_AMPLITUDE_AND_PHASE:
                num_images = 2
    
            count = 0
            while count < num_images:
                print('offset=%d'%(offset))
            
                ndim_struct = struct.Struct('H')
                ndimsize = struct.calcsize(ndim_struct.format)
                ndim = ndim_struct.unpack(msg[offset:offset + ndimsize])[0]
    
                dimStruct = struct.Struct('H'*int(ndim))
                dimsize = struct.calcsize(dimStruct.format)
                dimensions = dimStruct.unpack(msg[offset + ndimsize:offset + ndimsize + dimsize])
    
                offset = offset + ndimsize + dimsize
    
                if srcid == interface.SRCID_IMAGE_FOURIER:
                    dtype = np.complex64 
                    w, h = dimensions
                elif srcid == interface.SRCID_IMAGE_RAW:
                    dtype = np.uint8
                    w, h = dimensions
                #elif srcid == interface.SRCID_IMAGE_AMPLITUDE or srcid == interface.SRCID_IMAGE_PHASE or srcid == interface.SRCID_IMAGE_AMPLITUDE_AND_PHASE:
                else:
                    dtype = np.int8
                    w, h, z, l = dimensions
    
                outdata = np.fromstring(msg[offset:offset+(functools.reduce(lambda x,y: x*y, dimensions)*np.dtype(dtype).itemsize)], dtype=dtype).reshape(dimensions)
    
                offset += (functools.reduce(lambda x,y: x*y, dimensions)*np.dtype(dtype).itemsize)
                if PLOT:
                    if srcid == interface.SRCID_IMAGE_RAW:
                        axes.clear()
                        axes.imshow(outdata[:,:], extent=[0,h,0,w], aspect="auto")
                        axes.set_title('Max=%.3f'%(np.max(outdata[:,:])))
                    elif srcid == interface.SRCID_IMAGE_FOURIER:
                        axes.clear()
                        axes.imshow(outdata[:,:], extent=[0,h,0,w], aspect="auto")
                        axes.set_title('Max=%.3f'%(np.max(outdata[:,:])))
                    else:
                        axes.clear()
                        axes.imshow(outdata[:,:,0,0], extent=[0,h,0,w], aspect="auto")
                        axes.set_title('Max=%.3f'%(np.max(outdata[:,:,0,0])))
                    
                    plt.suptitle(repr(time.time()))
                    plt.draw()
                    plt.pause(0.001)

                count += 1
                

        print('End of DisplayThread')

    def connect_to_server(self, server, port):

        #headerStruct = struct.Struct('HHBIIIHH')

        totlen = 0

        count = 0

        ### Continous receive of data
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((server, port))
        self.readfds = [self.sock]

        ### Start Display Thread
        self.displaythread.start()
        length = None
        buf = b''
        data = b''
        msg=b''
        lasttime = time.time()
        meta = None
        totalbytes = 0
        while True:

            infds, outfds, errfds = select.select(self.readfds, [], [], 5)
            if not (infds or outfds or errfds):
                continue
            if self.exit: break

            for s in infds:
                if s is self.sock:
                    ### Get as much data as we can
                    packet = self.sock.recv(150995023)

                    if not packet:
                        self.exit = True
                        self.displayQ.put_nowait(None)
                        break
                    data += packet
                    datalen = len(data)

                    print('len packet= %d'%(len(packet)))
                    ### If he haven't processed the header/meta, then lets.
                    #if meta is None and datalen > struct.calcsize(headerStruct.format)+25:
                    if meta is None and datalen > struct.calcsize(headerStruct.format):
                       #packet = self.sock.recv(12)
                        #print("Recieve: %s"%(':'.join("{:02x}".format(ord(c)) for c in packet[0:50])))
                        msg_id, srcid, totalbytes = headerStruct.unpack(data[0:struct.calcsize(headerStruct.format)])
                        totalbytes += struct.calcsize(headerStruct.format)
                        meta = (msg_id, srcid)
                        print('msg_id=%d, srcid=%d, totalbytes=%d'%(msg_id, srcid, totalbytes))

                        if datalen >= totalbytes:  ### We have a complete packet stored.
                            msg = data[:totalbytes]
                            data = data[totalbytes:]
                            meta = None
                            totalbytes = 0
                            print('%.2f Hz'%(1/(time.time()-lasttime)))
                            lasttime = time.time()
                            #plt.show(block=False)
                            count+=1
                            self.displayQ.put_nowait(msg)
                            print('Full message received after getting meta: datalen=%d, datalen after=%d'%(datalen, len(data)))
                    else:

                        if datalen < totalbytes:
                            continue

                        ### We have a complete message
                        msg = data[:totalbytes]
                        data = data[totalbytes:]
                        print('Full message received: datalen=%d, datalen after=%d'%(datalen, len(data)))
                        meta = None
                        totalbytes = 0
                        self.displayQ.put_nowait(msg)
                        print('%.2f Hz'%(1/(time.time()-lasttime)))
                        lasttime = time.time()
                        count+=1
            if self.exit: break

        self.sock.close() 


if __name__ == "__main__":
    a = guiclient()
    host= 'localhost'
    port = 9997
    print("Client host:  %s: port: %d"%(host, port)) 
    a.connect_to_server(host, port) 
