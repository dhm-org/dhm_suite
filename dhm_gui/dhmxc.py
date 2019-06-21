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
from display_dhmxc import (guiclient)
from telemetry import (Tlm)

DHMXC_VERSION_STRING = "DHMx Camera Settings v0.9.9   06-20-2019"

HOST = socket.gethostbyname('localhost')
FRAME_SERVER_PORT = 2000
COMMAND_SERVER_PORT = 2001
TELEMETRY_SERVER_PORT = 2002


def SetCommandServerPort(port_num):
   global COMMAND_SERVER_PORT
   COMMAND_SERVER_PORT = int(port_num)

def SetFrameServerPort(port_num):
   global FRAME_SERVER_PORT
   FRAME_SERVER_PORT = int(port_num)

def SetTelemetryServerPort(port_num):
   global TELEMETRY_SERVER_PORT
   TELEMETRY_SERVER_PORT = int(port_num)

# This is a command that is used throughout DHMx and must be visible to all
# Classes and functions
# Command to be sent is in this format:
### dhm_command(server=HOST, port=PORT, cmdstr=cmd) ###
def CameraServerCommand(cmdstr):
    global w, COMMAND_SERVER_PORT

    try:
       cmdstr = cmdstr.strip()
       a = DHM_Command_Client(HOST, COMMAND_SERVER_PORT)
       cmd_ret = a.send(cmdstr)
       return cmd_ret
    except:
       print("Unable to send command - check camera server")
       return -1





class HologramImageProvider(QQuickImageProvider, QObject):
    def __init__(self):
        super(HologramImageProvider, self).__init__(QQuickImageProvider.Image)
        self.img = QImage(2048,2048, QImage.Format_Grayscale8)
        self.img.fill(QColor("black"))


    # Here is where the image will be filled
    def requestImage(self, p_str, size):
        try:
           # HOLOGRAM WINDOW
           if(w != None):
              if(w is not None and w.img_data is not None):
                 self.img = QImage(w.img_data,w.img_data.shape[1], w.img_data.shape[0], QImage.Format_RGB888)#Format_RGB888
        except NameError:
           OutputDebug("Hologram image subsystem not yet initialized...")
        if(size):
           size = self.img.size()

        if(size.width() > 0 and size.height() > 0):
           #self.img = self.img.scaled(63,63)#scale of 31.05%
           self.img = self.img.scaled(size.width(), size.height())
           
           #self.img = self.img.scaled(size.width(), size.height(), Qt.KeepAspectRatio())
        return self.img, self.img.size()





class MainWin(QObject):
    ## CONSTRUCTOR ##

   def __init__(self):
      super().__init__()
      global COMMAND_SERVER_PORT, FRAME_SERVER_PORT
      self.startup = True
      self.camera_server_port = COMMAND_SERVER_PORT
      self.camera_frame_port = FRAME_SERVER_PORT
      self.display_t = QThread()
      self.img_data = None
      engine.load('qt/DhmxCamera.qml')
      self.win = engine.rootObjects()[0]
      self.win.setProperty("title", DHMXC_VERSION_STRING)

      # Collect QObjects
      self.check_recording = self.win.findChild(QObject,"check_recording")
      self.label_width_data = self.win.findChild(QObject, "label_width_data")
      self.label_height_data = self.win.findChild(QObject, "label_height_data")
      self.label_timestamp_data = self.win.findChild(QObject, "label_timestamp_data")
      self.label_frame_id_data = self.win.findChild(QObject, "label_frame_id_data")
      self.label_set_fps_data = self.win.findChild(QObject, "label_set_fps_data")
      self.label_current_fps_data = self.win.findChild(QObject, "label_current_fps_data")
      self.button_apply = self.win.findChild(QObject, "button_apply")
      self.image_sample = self.win.findChild(QObject, "image_sample")
      self.textField_exposure = self.win.findChild(QObject, "textField_exposure")
      self.textField_gain = self.win.findChild(QObject, "textField_gain")
      self.slider_exposure = self.win.findChild(QObject, "slider_exposure")
      self.slider_gain = self.win.findChild(QObject,"slider_gain")

      # Connect QObject signals
      self.win.send_cmd.connect(CameraServerCommand)
      self.check_recording.qml_signal_recording.connect(self.ApplyRecording)

      # Start streaming images
      self.display_t = guiclient(HOST,FRAME_SERVER_PORT)
      self.display_t.start()
      self.BeginPlayback()

   def ApplyRecording(self, isRecording):
      if(isRecording):
         CameraServerCommand("ENABLE_RECORDING")    
      else:
         CameraServerCommand("DISABLE_RECORDING")


   # When this is called by the main window (signal/slot), this will start a 
   # series of events which will spawn Qt threads and begin the actual playback
   def BeginPlayback(self):
      self.display_t.sig_header.connect(self.UpdateHeaderInfo)
      self.display_t.sig_img_complete.connect(self.UpdateImage)
      self.display_t.start()


   #PYQT SLOT
   # Called by display.py, this receives the header information from the camera server
   # and displays it in the dhmxc window on the bottom
   def UpdateHeaderInfo(self, width, height, frameid, timestamp, gain_min, gain_max, exposure_min, exposure_max, gain, exposure, rate, measured_rate):
      self.label_width_data.setProperty("text",str(width))
      self.label_height_data.setProperty("text",str(height))
      self.label_timestamp_data.setProperty("text",str(timestamp))
      self.label_frame_id_data.setProperty("text",str(frameid))
      self.label_set_fps_data.setProperty("text",str(round(rate,2)))
      self.label_current_fps_data.setProperty("text",str(round(measured_rate,2)))
      self.win.setProperty("gain_min",gain_min)
      self.win.setProperty("gain_max",gain_max)
      self.win.setProperty("exposure_min",exposure_min)
      self.win.setProperty("exposure_max",exposure_max)
      if(self.startup):
         self.win.apply_settings_on_startup(gain,exposure)
         self.startup = False

   #PYQT SLOT
   # Called by raw_display.py.  When an image is finished being reconstructed
   # It writes to a file and then emits a signal that is received by this function
   def UpdateImage(self,timetag):
      self.img_data = self.display_t.outdata_RGB
      self.image_sample.reload()


### MAIN ####
## This will launch the Qt QML engine and launch the main QML window
if __name__ == "__main__":
    #Parse in arguments on launch
    parser = OptionParser()

    parser.add_option("-f","--frameserver", dest="frameServerPort",
                    help="This argument will override the default port for the Frame Server to a port of your choosing.")
    parser.add_option("-c","--cmdserver", dest="commandServerPort",
                    help="This argument will override the default port for the Command Server to a port of your choosing.")
    parser.add_option("-t","--tlmserver", dest="telemetryServerPort",
                    help="This argument will override the default port for the Telemetry Server to a port of your choosing.")

    # parse in the arguments
    (opts, args) = parser.parse_args()


    # Prepare the QML engine
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()


    provider_hologram = HologramImageProvider()
    engine.addImageProvider("Hologram", provider_hologram)

    # Set custom ports if specified
    if(opts.frameServerPort):
       SetFrameServerPort(opts.frameServerPort)

    if(opts.commandServerPort):
       SetCommandServerPort(opts.commandServerPort)

    if(opts.telemetryServerPort):
       SetTelemetryServerPort(opts.telemetryServerPort)

    w = MainWin()

    # Begin Qt Execution
    app.exec_()

    # Cleanup main thread
    sys.exit()
################################################################################
