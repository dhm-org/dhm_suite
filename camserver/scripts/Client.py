import sys
import signal
import select
import socket
import numpy as np
import pickle
import matplotlib.pyplot as plt
import time
from multiprocessing import Process, Queue
import struct
PLOT = True

headerStruct = struct.Struct('HHHBIIIHH')

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
            #for i in range(self.displayQ.qsize()-1):
            #    msg = self.displayQ.get()
            msg = self.displayQ.get()
            if msg is None:
                break

            w, h, compval, val, size, actualsize,ts, gain, ccdtemp = headerStruct.unpack(msg[0:struct.calcsize(headerStruct.format)])
            meta = (w, h, compval, val, size, actualsize,ts, gain, ccdtemp)
            offset = struct.calcsize(headerStruct.format) 
            print('offset=%d'%(offset))
            
            data = np.fromstring(msg[offset:offset+actualsize], dtype=np.uint8)
            
            if compval > 1:
                if mydata2.shape != (w,h):
                    mydata2 = np.ones(w*h, dtype=np.uint8) * 255
                self.restore_frame(data, meta, mydata2)
            else:
                mydata2 = data
            
            mydata = np.reshape(mydata2, (h,w))
            
            print("&&&&& Max=%f, Min=%f, QueueSize=%d"%(np.max(mydata[:,:]), np.min(mydata[:,:]), self.displayQ.qsize()))
            if PLOT:
                #plt.clf()
                for i in range(1):
                    #axes[i].imshow(mydata[:,:], extent=[0,w,0,h], aspect="auto", cmap='gray')
                    axes.clear()
                    axes.imshow(mydata[:,:], extent=[0,h,0,w], aspect="auto")
                    axes.set_title('Max=%.3f'%(np.max(mydata[:,:])))

                plt.suptitle(repr(time.time()))
                plt.draw()
                #plt.show(block=False)
                plt.pause(0.001)
                

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

            infds, outfds, errfds = select.select(self.readfds, [] , [], 5)
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

                    ### If he haven't processed the header/meta, then lets.
                    #if meta is None and datalen > struct.calcsize(headerStruct.format)+25:
                    if meta is None and datalen > struct.calcsize(headerStruct.format):
                       #packet = self.sock.recv(12)
                        #print("Recieve: %s"%(':'.join("{:02x}".format(ord(c)) for c in packet[0:50])))
                        w, h, compval,val, size, actualsize, ts, gain, ccdtemp = headerStruct.unpack(data[0:struct.calcsize(headerStruct.format)])
                        totalbytes =  actualsize + struct.calcsize(headerStruct.format)
                        meta = (w, h, compval, val, size,actualsize, ts, gain, ccdtemp)
                        print('w=%d, h=%d, compval=%d, val=%d, size=%d, actualsize=%d, ts=%d, gain=%d, ccdtemp=%d', w, h, compval, val, size, actualsize, ts, gain, ccdtemp)

                        if datalen >= totalbytes:  ### We have a complete packet stored.
                            msg = data[:totalbytes]
                            data = data[totalbytes:]
                            meta = None
                            totalbytes = 0
                            print('Counter=%d, Queue.Size=%d'%(count, self.displayQ.qsize()))
                            print('%.2f Hz'%(1/(time.time()-lasttime)))
                            lasttime = time.time()
                            #plt.show(block=False)
                            count+=1
                            if self.displayQ.qsize() == 0:
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
                        if self.displayQ.qsize() == 0:
                            self.displayQ.put_nowait(msg)
                        print('Counter=%d, Queue.Size=%d'%(count, self.displayQ.qsize()))
                        print('%.2f Hz'%(1/(time.time()-lasttime)))
                        lasttime = time.time()
                        count+=1
            if self.exit: break

        self.sock.close() 


if __name__ == "__main__":
    a = guiclient()
    host= '127.0.0.1' #socket.gethostname()
    port = 2000
    print("Client host:  %s: port: %d"%(host, port)) 
    a.connect_to_server(host, port) 
