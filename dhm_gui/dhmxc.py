#######!/usr/bin/python3 -B
# -*- coding: utf-8 -*-
# General Python

# For Caltech use only for testing purposes.

# Copyright 2019, by the California Institute of Technology. 
# ALL RIGHTS RESERVED. United States Government Sponsorship acknowledged. 
# Any commercial use must be negotiated with the Office of Technology 
# Transfer at the California Institute of Technology.
 
# This software may be subject to U.S. export control laws. By accepting 
# this software, the user agrees to comply with all applicable U.S. export 
# laws and regulations. User has the responsibility to obtain export licenses, 
# or other export authority as may be required before exporting such 
# information to foreign countries or providing access to foreign persons.

import os, sys, re, time, random
import threading
from multiprocessing import Process, Queue
import queue as queue
import select
import signal
import ntpath
import socket
import math
import logging

from threading import Timer
from datetime import datetime
from optparse import OptionParser

#Qt5 Specific
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtQuick import *
from PyQt5.QtQml import *
import PyQt5.QtMultimedia

#DHM Specific (Please be sure to have all DHM related files added into the DHMx directory
from dhm_cmd_client_server import (DHM_Command_Client)
from display import (guiclient)
from telemetry import (Tlm)

# Custom filedialog windows (QML's default implementation does not satisfy DHMx needs)
import dhmx_filedialog


HOST = socket.gethostbyname('localhost')
CAMERA_SERVER_PORT = 2001



def SetCameraServerPort(port_num):
   global CAMERA_SERVER_PORT
   CAMERA_SERVER_PORT = int(port_num)


# This is a command that is used throughout DHMx and must be visible to all
# Classes and functions
# Command to be sent is in this format:
### dhm_command(server=HOST, port=PORT, cmdstr=cmd) ###
def CameraServerCommand(cmdstr):
    global w, CAMERA_SERVER_PORT

    try:
       a = DHM_Command_Client(HOST, CAMERA_SERVER_PORT)
       cmd_ret = a.send(cmdstr)
       return cmd_ret
    except:
       print("Unable to send command - check camera server")
       return -1



class MainWin(QObject):
    ## CONSTRUCTOR ##

   def __init__(self):
      super().__init__()
      global CAMERA_SERVER_PORT
      self.camera_server_port = CAMERA_SERVER_PORT
      engine.load('qt/DhmxCamera.qml')
      self.win = engine.rootObjects()[0]

      # Collect QObjects
      self.check_recording = self.win.findChild(QObject,"check_recording")
      self.button_apply = self.win.findChild(QObject, "button_apply")

      # Connect QObject signals
      self.button_apply.clicked.connect(self.ApplySettings)


   def ApplySettings(self):
      if(self.check_recording.property("checked")):
         CameraServerCommand("ENABLE_RECORDING")    
      else:
         CameraServerCommand("DISABLE_RECORDING")



### MAIN ####
## This will launch the Qt QML engine and launch the main QML window
if __name__ == "__main__":
    #Parse in arguments on launch
    parser = OptionParser()

    parser.add_option("-p","--port", dest="port",
                    help="Will display a window at launch of DHMx to specify custom ports for the program.")

    # parse in the arguments
    (opts, args) = parser.parse_args()


    # Prepare the QML engine
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Set camera port if specified
    if(opts.port):
       SetCameraServerPort(opts.port)

    w = MainWin()

    # Begin Qt Execution
    app.exec_()

    # Cleanup main thread
    sys.exit()
################################################################################
