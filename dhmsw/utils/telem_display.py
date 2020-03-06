import sys
import functools
import signal
import select
import socket
import numpy as np
import pickle
import matplotlib.pyplot as plt
import time
import datetime
from multiprocessing import Process, Queue
sys.path.append('../dhmsw/')
import interface
import telemetry_iface_ag
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

        if PLOT:
            f, axes = plt.subplots(sharex=True)
            for i in range(1):
                #axes[i].imshow(z, extent=[0,2448,0,2050], aspect="auto", cmap='gray')
                axes.clear()
                #axes.imshow(z, extent=[0,2448,0,2050], aspect="auto", cmap='gray')

        reconst_telemetry = telemetry_iface_ag.Reconstruction_Telemetry()
        heartbeat_telemetry = telemetry_iface_ag.Heartbeat_Telemetry()
        framesource_telemetry = telemetry_iface_ag.Framesource_Telemetry()
        datalogger_telemetry = telemetry_iface_ag.Datalogger_Telemetry()
        guiserver_telemetry = telemetry_iface_ag.Guiserver_Telemetry()
        session_telemetry = telemetry_iface_ag.Session_Telemetry()
        hologram_telemetry = telemetry_iface_ag.Hologram_Telemetry()
        fouriermask_telemetry = telemetry_iface_ag.Fouriermask_Telemetry()

        while True:
            msg = self.displayQ.get()
            if msg is None:
                break

            #print("**************** Display Thread")   
            msgid, srcid, totalbytes= headerStruct.unpack(msg[0:struct.calcsize(headerStruct.format)])
            meta = (msgid, srcid, totalbytes)
            offset = struct.calcsize(headerStruct.format) 
            #print('offset=%d'%(offset))
            data = None
            if srcid == interface.SRCID_TELEMETRY_RECONSTRUCTION:
                print('Received RECONSTRUCTION Telemetry')    
                data = reconst_telemetry.unpack_from(msg, offset=offset)
            elif srcid == interface.SRCID_TELEMETRY_HEARTBEAT:
                data = heartbeat_telemetry.unpack_from(msg, offset=offset)
            elif srcid == interface.SRCID_TELEMETRY_FRAMESOURCE:
                data = framesource_telemetry.unpack_from(msg, offset=offset)
                print('Framesource state: ', data.state)
            elif srcid == interface.SRCID_TELEMETRY_SESSION:
                data = session_telemetry.unpack_from(msg, offset=offset)
            elif srcid == interface.SRCID_TELEMETRY_DATALOGGER:
                data = datalogger_telemetry.unpack_from(msg, offset=offset)
            elif srcid == interface.SRCID_TELEMETRY_HOLOGRAM:
                data = hologram_telemetry.unpack_from(msg, offset=offset)
            elif srcid == interface.SRCID_TELEMETRY_GUISERVER:
                data = guiserver_telemetry.unpack_from(msg, offset=offset)
            elif srcid == interface.SRCID_TELEMETRY_FOURIERMASK:
                data = fouriermask_telemetry.unpack_from(msg, offset=offset)
                if PLOT:
                    mask = np.frombuffer(data.mask, dtype=np.uint8).reshape((2048,2048))
                    #mask = np.asarray(data.mask,dtype=np.int8).reshape((2048,2048))
                    axes.clear()
                    #axes.imshow(mask[:,:], extent=[2048,0,0,2048], aspect="auto")
                    axes.imshow(mask[:,:], aspect="auto")
                    plt.suptitle(repr(time.time()))
                    #axes.set_ylim(axes.get_ylim()[::-1])
                    plt.draw()
                    plt.pause(0.001)
                    
            else:
                print('Unknown Telemetry')    
            if data and srcid != interface.SRCID_TELEMETRY_HEARTBEAT:
                print(time.time(), datetime.datetime.now())
                print(data)
                pass

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
                    packet = self.sock.recv(255)

                    if not packet:
                        self.exit = True
                        self.displayQ.put_nowait(None)
                        break
                    data += packet
                    datalen = len(data)

                    #print('len packet= %d'%(len(packet)))
                    ### If he haven't processed the header/meta, then lets.
                    #if meta is None and datalen > struct.calcsize(headerStruct.format)+25:
                    if meta is None and datalen >= struct.calcsize(headerStruct.format):
                       #packet = self.sock.recv(12)
                        #print("Recieve: %s"%(':'.join("{:02x}".format(ord(c)) for c in packet[0:50])))
                        msg_id, srcid, totalbytes = headerStruct.unpack(data[0:struct.calcsize(headerStruct.format)])
                        totalbytes += struct.calcsize(headerStruct.format)
                        meta = (msg_id, srcid)
                        #print('msg_id=%d, srcid=%d, totalbytes=%d'%(msg_id, srcid, totalbytes))

                        if datalen >= totalbytes:  ### We have a complete packet stored.
                            msg = data[:totalbytes]
                            data = data[totalbytes:]
                            meta = None
                            totalbytes = 0
                            #print('%.2f Hz'%(1/(time.time()-lasttime)))
                            lasttime = time.time()
                            #plt.show(block=False)
                            count+=1
                            self.displayQ.put_nowait(msg)
                            #print('Full message received after getting meta: datalen=%d, datalen after=%d'%(datalen, len(data)))
                    else:

                        if datalen < totalbytes:
                            continue

                        ### We have a complete message
                        msg = data[:totalbytes]
                        data = data[totalbytes:]
                        #print('Full message received: datalen=%d, datalen after=%d'%(datalen, len(data)))
                        meta = None
                        totalbytes = 0
                        self.displayQ.put_nowait(msg)
                        #print('%.2f Hz'%(1/(time.time()-lasttime)))
                        lasttime = time.time()
                        count+=1
            if self.exit: break

        self.sock.close() 


if __name__ == "__main__":
    a = guiclient()
    host= socket.gethostbyname('localhost')
    port = 9996
    print("Client host:  %s: port: %d"%(host, port)) 
    a.connect_to_server(host, port) 
