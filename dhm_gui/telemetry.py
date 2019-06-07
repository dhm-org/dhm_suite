import sys
import functools
import signal
import select
import socket
import numpy as np
import pickle
import time
from multiprocessing import Process, Queue
import interface
import telemetry_iface_ag
import struct

import datetime

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtQuick import *
from PyQt5.QtQml import *



headerStruct = struct.Struct('III')

class Tlm(QThread):
    tlm_data_reconst = pyqtSignal(telemetry_iface_ag.Reconstruction_Telemetry.Data)
    tlm_data_heartbeat = pyqtSignal(telemetry_iface_ag.Heartbeat_Telemetry.Data)
    tlm_data_framesource = pyqtSignal(telemetry_iface_ag.Framesource_Telemetry.Data)
    tlm_data_session = pyqtSignal(telemetry_iface_ag.Session_Telemetry.Data)
    tlm_data_logging = pyqtSignal(telemetry_iface_ag.Datalogger_Telemetry.Data)
    tlm_data_hologram = pyqtSignal(telemetry_iface_ag.Hologram_Telemetry.Data)
    tlm_data_guiserver = pyqtSignal(telemetry_iface_ag.Guiserver_Telemetry.Data)

    data_recv = pyqtSignal(bytes)

    thread_msg = None

    def __init__(self):
        QThread.__init__(self)
        super().__init__()
        self.sock = None
        self.exit = False
        self.host= socket.gethostbyname('localhost')
        self.port = 9996
        self.maxlen = 150995023

        self.msg = None
        self.msgid = None
        self.srcid = None
        self.totalbytes = None
        self.meta = None
        self.offset = None

        self.reconst_telemetry = telemetry_iface_ag.Reconstruction_Telemetry()
        self.heartbeat_telemetry = telemetry_iface_ag.Heartbeat_Telemetry()
        self.framesource_telemetry = telemetry_iface_ag.Framesource_Telemetry()
        self.datalogger_telemetry = telemetry_iface_ag.Datalogger_Telemetry()
        self.guiserver_telemetry = telemetry_iface_ag.Guiserver_Telemetry()
        self.session_telemetry = telemetry_iface_ag.Session_Telemetry()
        self.hologram_telemetry = telemetry_iface_ag.Hologram_Telemetry()


        for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
            signal.signal(sig, self.signal_handler)



    def signal_handler(self, signal, frame):
        self.exit = True


    def run(self):
        ### Continous receive of data
        try:
           self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           self.sock.connect((self.host, self.port))
           self.readfds = [self.sock]
        except socket.error as e:
           print("Telemetry could not establish communication with dhmsw.  Please check your connection.")
           if self.sock:
              self.sock.close()
              self.sock = None

        ### Start Telemetry Thread
        length = None
        buf = b''
        data = b''
        msg=b''
        meta = None
        totalbytes = 0
        while True:
            try:
               infds, outfds, errfds = select.select(self.readfds, [], [],5)
              

               if not (infds or outfds or errfds):
                   continue
               if self.exit: break

               for s in infds:
                   if s is self.sock:
                       ### Get as much data as we can
                       packet = self.sock.recv(255) #possible 4194304

                       if not packet:
                           self.exit = True
                           break

                       data += packet
                       datalen = len(data)

                       ### If he haven't processed the header/meta, then lets.
                       #if meta is None and datalen > struct.calcsize(headerStruct.format)+25:
                       if meta is None and datalen >= struct.calcsize(headerStruct.format):
                          msg_id, srcid, totalbytes = headerStruct.unpack(data[0:struct.calcsize(headerStruct.format)])
                          totalbytes += struct.calcsize(headerStruct.format)
                          meta = (msg_id, srcid)

                          # Complete packet here - prep and send
                          if datalen >= totalbytes:  
                             msg = data[:totalbytes]
                             data = data[totalbytes:]
                             meta = None
                             totalbytes = 0
                             self.unpack_message(msg)

                       else:
                          if datalen < totalbytes:
                             continue

                          # We have a complete message here
                          msg = data[:totalbytes]
                          data = data[totalbytes:]
                          meta = None
                          totalbytes = 0
                          self.unpack_message(msg)

            except:
               print("Could not run select for telemetry polling.  Please check your connection.")
               sys.exit()
              #break
            if self.exit: break

        self.sock.close() 


    def unpack_message(self,msg):

        self.msg = msg
        self.msgid, self.srcid, self.totalbytes= headerStruct.unpack(self.msg[0:struct.calcsize(headerStruct.format)])
        self.meta = (self.msgid, self.srcid, self.totalbytes)
        self.offset = struct.calcsize(headerStruct.format) 
       

        if self.srcid == interface.SRCID_TELEMETRY_RECONSTRUCTION:  
                   #print("Received RECONST telemetry - time: ",datetime.datetime.now())
                   self.tlm_data_reconst.emit(self.reconst_telemetry.unpack_from(self.msg, offset=self.offset))

        elif self.srcid == interface.SRCID_TELEMETRY_HEARTBEAT:
                   #print("Received HEARTBEAT telemetry - time: ",datetime.datetime.now())
                   self.tlm_data_heartbeat.emit(self.heartbeat_telemetry.unpack_from(self.msg, offset=self.offset))

        elif self.srcid == interface.SRCID_TELEMETRY_FRAMESOURCE:
                   #print("Received FRAMESOURCE telemetry - Time: ",datetime.datetime.now())
                   self.tlm_data_framesource.emit(self.framesource_telemetry.unpack_from(self.msg, offset=self.offset))

        elif self.srcid == interface.SRCID_TELEMETRY_SESSION:
                   #print("Received SESSION telemetry - Time: ",datetime.datetime.now())
                   self.tlm_data_session.emit(self.session_telemetry.unpack_from(self.msg, offset=self.offset))

        elif self.srcid == interface.SRCID_TELEMETRY_DATALOGGER:
                   #print("Received DATALOGGER telemetry - Time: ",datetime.datetime.now())
                   self.tlm_data_logging.emit(self.datalogger_telemetry.unpack_from(self.msg, offset=self.offset))

        elif self.srcid == interface.SRCID_TELEMETRY_HOLOGRAM:
                   #print("Received HOLOGRAM telemetry - Time: ",datetime.datetime.now())
                   self.tlm_data_hologram.emit(self.hologram_telemetry.unpack_from(self.msg, offset=self.offset))

        elif self.srcid == interface.SRCID_TELEMETRY_GUISERVER:
                   #print("Received GUISERVER telemetry - Time: ",datetime.datetime.now())
                   self.tlm_data_guiserver.emit(self.guiserver_telemetry.unpack_from(self.msg, offset=self.offset))

