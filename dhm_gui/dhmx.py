#!/usr/bin/python3 -B
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


DHMX_VERSION_STRING = "DHMx v0.10.2  08-21-2019"


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
import subprocess
from PIL import Image, ImageDraw

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
import video_converter as vc

# Custom filedialog windows (QML's default implementation does not satisfy DHMx needs)
import dhmx_filedialog

# Import Dhmx-Camera.  This is actually a standalone program that can be launched on its own
import dhmxc as dhmxc

#GLOBALS
RUNNING_PATH = os.path.split(os.path.abspath(__file__))
HOST = socket.gethostbyname('localhost')
PORT = 10000
DHM_TELEMETRY_SERVER_PORT = 9996
FRAME_SERVER_PORT = 2000
COMMAND_SERVER_PORT = 2001
TELEMETRY_SERVER_PORT = 2002
RAW_FRAME_PORT = 9995
RECONST_AMP_FRAME_PORT = 9994
RECONST_INT_FRAME_PORT = 9997
RECONST_PHASE_FRAME_PORT = 9998
FOURIER_FRAME_PORT = 9993
FRAMESOURCE_MODE = "None"
MAX_WAVELENGTH = 0
MAX_PROPAGATION_DISTANCE = 0
CAMERA_CONVERSION_RATIO = 0.50
open_flag = False
w = None
tlm = None
tlm_manager = None



# Setting of custom ports if launch arguments are given
def SetCommandServerPort(port_num):
   global COMMMAND_SERVER_PORT
   COMMAND_SERVER_PORT = int(port_num)
def SetFrameServerPort(port_num):
   global FRAME_SERVER_PORT
   FRAME_SERVER_PORT = int(port_num)
def SetTelemetryServerPort(port_num):
   global TELEMETRY_SERVER_PORT
   TELEMETRY_SERVER_PORT = int(port_num)
def SetDhmCommandServerPort(port_num):
   global PORT
   PORT = int(port_num)
def SetDhmTelemetryServerPort(port_num):
   global DHM_TELEMETRY_SERVER_PORT
   DHM_TELEMETRY_SERVER_PORT = int(port_num)
def SetPhasePort(port_num):
   global RECONST_PHASE_FRAME_PORT
   RECONST_PHASE_FRAME_PORT = int(port_num)
def SetIntensityPort(port_num):
   global RECONST_INT_FRAME_PORT
   RECONST_INT_FRAME_PORT = int(port_num)
def SetRawPort(port_num):
   global RAW_FRAME_PORT
   RAW_FRAME_PORT = int(port_num)
def SetAmplitudePort(port_num):
   global RECONST_AMP_FRAME_PORT
   RECONST_AMP_FRAME_PORT = int(port_num)
def SetFourierPort(port_num):
   global FOURIER_FRAME_PORT
   FOURIER_FRAME_PORT = int(port_num)
# End Setting of custom ports

# Loading and saving files for DHMx
# DHMx will save files as a *.cfg file in plain text.
# The user has the option to manually modify the configuration files if they so choose as well
def LoadFile(file_type,x,y,path,title):
   if(file_type == "ses"):
      # For Reconst Config files
      try:
         fd = dhmx_filedialog.CreateFileDialog(x, y, path, title, "load_ses")
         if(fd.GetFilename() != ''):
            file = open(fd.GetFilename(),"r")
            return file.read()
         else:
            # Return something benign if nothing exists 
            return "session"
      except:
         print("ERROR: Could not load session file...")
         return "session"

   if(file_type == "cfg"):
      # For Reconst Config files
      try:
         fd = dhmx_filedialog.CreateFileDialog(x, y, path, title, "load_cfg")
         if(fd.GetFilename() != ''):
            file = open(fd.GetFilename(),"r")
            return file.read()
         else:
            # Return something benign if nothing exists 
            return "reconst"
      except:
           print("ERROR: Could not load configuration file...")
           return "reconst"


def SaveFile(file_type,cfg_file, x, y, path, title):
   if(file_type == "ses"):
      # For Reconst Config files
      try:
         fd = dhmx_filedialog.CreateFileDialog(x, y, path, title, "save_ses")
         if(fd.GetFilename() != ''):
            if ".ses" in fd.GetFilename():
               file = open(fd.GetFilename(),"w")
            else:
               file = open(fd.GetFilename()+".ses","w")
            file.writelines(cfg_file)
            file.close()
      except:
         print("ERROR: Could not save session file.")

   if(file_type == "cfg"):
      try:
         # For Reconst Config files
         fd = dhmx_filedialog.CreateFileDialog(x, y, path, title, "save_cfg")
         if(fd.GetFilename() != ''):
            if ".cfg" in fd.GetFilename():
               file = open(fd.GetFilename(),"w")
            else:
               file = open(fd.GetFilename()+".cfg","w")
            file.writelines(cfg_file)
            file.close()
      except:
         print("ERROR: Could not save configuration file.")





class TelemetryManager(QObject):
   # This type of PyQt signal takes in a string for the key and an object for any value
   # this signal will be emitted and picked up by all the windows and filtered to 
   # update the windows dynamically
   sig_callback = pyqtSignal(str, object)

   def __init__(self,tlm):
      super().__init__()
  
      self.tlm  = tlm

      # Below are Dictionary objects which will store the telemetry
      self.heartbeat = {"timestamp" :                       None,
                        "status" :                          None,
                        "status_msg" :                      None,
                        "datalogger_status" :               None,
                        "controller_status" :               None,
                        "guiserver_status" :                None,
                        "reconstructor_status" :            None,
                        "framesource_status" :              None
                       }

      self.session = {"name" :                              None,
                      "description" :                       None,
                      "num_wavelength" :                    None,
                      "wavelength_1" :                      None,
                      "wavelength_2" :                      None,
                      "wavelength_3" :                      None,
                      "dx" :                                None,
                      "dy" :                                None,
                      "crop_fraction" :                     None,
                      "rebin_factor" :                      None,
                      "lens_focal_length" :                 None,
                      "lens_numerical_aperture" :           None,
                      "lens_system_magnification" :         None,
                      "status_msg" :                        None
                     }

      self.hologram = {"num wavelength" :                   None,
                       "wavelength" :                       None,
                       "dx" :                               None,
                       "dy" :                               None,
                       "crop_fraction" :                    None,
                       "rebin_factor" :                     None,
                       "bgd_sub" :                          None,
                       "bgd_file" :                         None
                      }

      self.reconstruction = {"num_propagation_distance" :   None,
                             "propagation_distance_1" :     None,
                             "propagation_distance_2" :     None,
                             "propagation_distance_3" :     None,
                             "compute_spectral_peak" :      None,
                             "compute_digital_phase_mask" : None,
                             "processing_mode" :            None,
                             "num_chromatic_shift" :        None,
                             "chromatic_shift_1" :          None,
                             "chromatic_shift_2" :          None,
                             "ref_holo_path" :              None,
                             "ref_holo_enable" :            None,
                             "ref_holo_averaging_sec" :     None,
                             "ref_holo_averaging_enabled" : None,
                             "phase_unwrapping_enabled" :   None,
                             "phase_unwrapping_algorithm" : None,
                             "fitting_mode" :               None,
                             "fitting_method" :             None,
                             "fitting_order" :              None,
                             "fitting_apply" :              None,
                             "reset_phase_mask" :           None,
                             "roi_offset_x" :               None,
                             "roi_offset_y" :               None,
                             "roi_size_x" :                 None,
                             "roi_size_y" :                 None,
                             "store_files" :                None,
                             "center_image" :               None,
                             "center_image_and_tilt" :      None,
                             "center_max_value" :           None,
                             "center_wide_spectrum" :       None,
                             "status_msg" :                 None
                            }

      self.framesource = {"state" :                         None,
                          "mode" :                          None,
                          "file_path" :                     None,
                          "current_file" :                  None,
                          "status_msg" :                    None
                         }

      self.datalogger = {"enabled" :                        None,
                         "rootpath" :                       None,
                         "status_msg" :                     None
                        }

      self.guiserver = {"ports" :                           None,
                        "connection_status" :               None,
                        "status_msg" :                      None
                       }

      # Connect signals that will be used throughout DHMx.  Currently
      # The two signals are Propagation distance and wavelength.
      # When a reconst or session is called (or when telemetry is received
      # by a completed command) these signals will go to their appropriate
      # slots which will then call  a callback method which will emit a
      # global signal for change across all of DHMx.  It is then that
      # Any window that requires propagation distance or wavelength, will
      # update dynamically.
      self.tlm.DhmxTlm.tlm_data_session.connect(self.UpdateWavelength)
      self.tlm.DhmxTlm.tlm_data_reconst.connect(self.UpdatePropDistance)
      self.tlm.DhmxTlm.tlm_data_framesource.connect(self.UpdateFramesource)

      print("DHMx: Telemetry Monitor launched.")


   def Callback(self, key, value):
       self.sig_callback.emit(key,value)


   def UpdateWavelength(self,tlm_data):
       self.session["num_wavelength"] = tlm_data.num_wavelength
       self.Callback("num_wavelength", self.session["num_wavelength"])
      

   def UpdatePropDistance(self,tlm_data):
       self.reconstruction["num_propagation_distance"] = tlm_data.num_propagation_distance
       self.Callback("num_propagation_distance", self.reconstruction["num_propagation_distance"])


   def UpdateFramesource(self,tlm_data):
       self.framesource["state"] = tlm_data.state
       self.Callback("state", self.framesource["state"])


   #TODO: Below is future functionality as the telemetry manager grows
   # As of right now, it's not important to implement yet.
   def GetTlm(self, tlm_dict, key): pass
   def SetTlm(self, tlm_dict, key): pass

   def UpdateHeartbeat(self): pass
   def UpdateSession(self): pass
   def UpdateHologram(self): pass
   def UpdateReconstruction(self): pass
   def UpdateDatalogger(self): pass
   def UpdateGuiserver(self): pass

   def UpdateTlm(self, tlm_dict): pass
   def UpdateAll(self): pass




class UpdateWavelengthAndProp(QObject):
   sig_wl = pyqtSignal(int)
   sig_prop = pyqtSignal(int)


   def __init__(self):
      super().__init__()
      self.max_wl = 0
      self.max_prop = 0


   def SetMaxWl(self,val):
      self.max_wl = val
      self.sig_wl.emit(self.max_wl)


   def SetMaxProp(self,val):
      self.max_prop = val
      self.sig_prop.emit(self.max_prop)


   def UpdateAll(self):
      DhmCommand("reconst")
      time.sleep(0.100)
      DhmCommand("session")
      self.sig_wl.emit(self.max_wl)
      self.sig_prop.emit(self.max_prop)


   def GetMaxWl(self):
      return self.max_wl


   def GetMaxPropDist(self):
      return self.max_prop






def OutputDebug(output):
   if(opts.verbose):
      print("DHMx DEBUG: ",output)
   if(opts.logging):
      logging.debug("DHMX DEBUG "+str(datetime.utcnow())+" : "+output)
   else:
      # verbose not selected, do not output
      return




#FML: EXPERIMENTAL
class FourierImageProvider(QQuickImageProvider, QObject):
    def __init__(self):
        super(FourierImageProvider, self).__init__(QQuickImageProvider.Image)
        self.img = QImage(2048,2048, QImage.Format_RGBA8888)
        self.img.fill(QColor("black"))

    # Here is where the image will be filled
    def requestImage(self, p_str, size):
        try:
           # FOURIER WINDOW
           if(w != None):
              if(w.FourierWin is not None and w.FourierWin.img_data is not None):
                 self.img = QImage(w.FourierWin.img_data,w.FourierWin.img_data.shape[1], w.FourierWin.img_data.shape[0], QImage.Format_RGB888)

        except NameError:
           OutputDebug("Fourier image subsystem not yet initialized...")
        if(size):
           size = self.img.size()

        if(size.width() > 0 and size.height() > 0):
           self.img = self.img.scaled(size.width(), size.height(), Qt.KeepAspectRatio())
        return self.img, self.img.size()






class PhaseImageProvider(QQuickImageProvider, QObject):
    def __init__(self):
        super(PhaseImageProvider, self).__init__(QQuickImageProvider.Image)
        self.img = QImage(2048,2048, QImage.Format_RGBA8888)
        self.img.fill(QColor("black"))


    # Here is where the image will be filled
    def requestImage(self, p_str, size):
        try:
           # PHASE WINDOW
           if(w != None):
              if(w.PhaseWin is not None and w.PhaseWin.img_data is not None):
                 self.img = QImage(w.PhaseWin.img_data,w.PhaseWin.img_data.shape[1], w.PhaseWin.img_data.shape[0], QImage.Format_RGB888)

        except NameError:
           OutputDebug("Phase image subsystem not yet initialized...")
        if(size):
           size = self.img.size()

        if(size.width() > 0 and size.height() > 0):
           self.img = self.img.scaled(size.width(), size.height(), Qt.KeepAspectRatio())
        return self.img, self.img.size()






class AmplitudeImageProvider(QQuickImageProvider, QObject):
    def __init__(self):
        super(AmplitudeImageProvider, self).__init__(QQuickImageProvider.Image)
        self.img = QImage(2048,2048, QImage.Format_RGBA8888)
        self.img.fill(QColor("black"))


    # Here is where the image will be filled
    def requestImage(self, p_str, size):
        try:
           # AMPLITUDE WINDOW
           if(w != None):
              if(w.AmplitudeWin is not None and w.AmplitudeWin.img_data is not None):
                 self.img = QImage(w.AmplitudeWin.img_data,w.AmplitudeWin.img_data.shape[1], w.AmplitudeWin.img_data.shape[0], QImage.Format_RGB888)

        except NameError:
           OutputDebug("Amplitude image subsystem not yet initialized...")
        if(size):
           size = self.img.size()

        if(size.width() > 0 and size.height() > 0):
           self.img = self.img.scaled(size.width(), size.height(), Qt.KeepAspectRatio())
        return self.img, self.img.size()






class IntensityImageProvider(QQuickImageProvider, QObject):
    def __init__(self):
        super(IntensityImageProvider, self).__init__(QQuickImageProvider.Image)
        self.img = QImage(2048,2048, QImage.Format_RGBA8888)
        self.img.fill(QColor("black"))


    # Here is where the image will be filled
    def requestImage(self, p_str, size):
        try:
           # AMPLITUDE WINDOW
           if(w != None):
              if(w.IntensityWin is not None and w.IntensityWin.img_data is not None):
                 self.img = QImage(w.IntensityWin.img_data,w.IntensityWin.img_data.shape[1], w.IntensityWin.img_data.shape[0], QImage.Format_RGB888)

        except NameError:
           OutputDebug("Amplitude image subsystem not yet initialized...")
        if(size):
           size = self.img.size()

        if(size.width() > 0 and size.height() > 0):
           self.img = self.img.scaled(size.width(), size.height(), Qt.KeepAspectRatio())
        return self.img, self.img.size()






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
              if(w.HologramWin is not None and w.HologramWin.img_data is not None):
                 self.img = QImage(w.HologramWin.img_data,w.HologramWin.img_data.shape[1], w.HologramWin.img_data.shape[0], QImage.Format_RGB888)#Format_RGB888
        except NameError:
           OutputDebug("Hologram image subsystem not yet initialized...")
        if(size):
           size = self.img.size()

        if(size.width() > 0 and size.height() > 0):
           #self.img = self.img.scaled(63,63)#scale of 31.05%
           self.img = self.img.scaled(size.width(), size.height())
           
           #self.img = self.img.scaled(size.width(), size.height(), Qt.KeepAspectRatio())
        return self.img, self.img.size()






# This is a command that is used throughout DHMx and must be visible to all
# Classes and functions
# Command to be sent is in this format:
### dhm_command(server=HOST, port=PORT, cmdstr=cmd) ###
def DhmCommand(cmdstr):
    global w
    OutputDebug("Sending Command to DHMSW...")
    try:
       a = DHM_Command_Client(HOST, PORT)
       OutputDebug("Command is: "+cmdstr)

       # Special commands
       # TODO: Make a better scheme for this...
       if(cmdstr.lower() == "framesource mode=file"):
          SetFrameSourceMode("file")
       if(cmdstr.lower() == "framesource mode=camera"):
          SetFrameSourceMode("camera")

       cmd_ret = a.send(cmdstr)
       if(w != None):
          w.text_status.setProperty("text","Command Received: "+cmd_ret.decode("ASCII"))
       return cmd_ret
    except:
       print("Unable to send command - check dhmsw")
       return -1





# This is a command that is used throughout DHMx and must be visible to all
# Classes and functions
# Command to be sent is in this format:
### dhm_command(server=HOST, port=PORT, cmdstr=cmd) ###
def CameraServerCommand(cmdstr):
    global w
    OutputDebug("Sending Command to Camera Server...")
    try:
       a = DHM_Command_Client(HOST, COMMAND_SERVER_PORT)
       OutputDebug("Command is: "+cmdstr)

       cmd_ret = a.send(cmdstr)
       if(w != None):
          w.text_status.setProperty("text","Command Received: "+cmd_ret.decode("ASCII"))
       return cmd_ret
    except:
       print("Unable to send command - check dhmsw")
       return -1






def SetFrameSourceMode(mode):
    global FRAMESOURCE_MODE
    FRAMESOURCE_MODE = mode
    if(w.FourierWin != None):
       w.FourierWin.label_source.setProperty("text",FRAMESOURCE_MODE)
    if(w.PhaseWin != None):
       w.PhaseWin.label_source.setProperty("text",FRAMESOURCE_MODE)
    if(w.AmplitudeWin != None):
       w.AmplitudeWin.label_source.setProperty("text",FRAMESOURCE_MODE)
    if(w.HologramWin != None):
       w.HologramWin.label_source.setProperty("text",FRAMESOURCE_MODE)
    return FRAMESOURCE_MODE






def GetFrameSourceMode():
   global FRAMESOURCE_MODE
   return FRAMESOURCE_MODE






def GetFrameSourceMode():
    return FRAMESOURCE_MODE







class DhmxTelemetry(QThread):
   def __init__(self):
      super().__init__()
      global w, DHM_TELEMETRY_SERVER_PORT
      try:
         self.DhmxTlm = Tlm()
         self.DhmxTlm.port = DHM_TELEMETRY_SERVER_PORT
         self.DhmxTlm.start()
      except OSError as e:
         print("Could not launch the Telemetry thread.")
          
 






class FourierWin(QObject):
    def __init__(self,tlm):
       super().__init__()
       global w
       self.tlm = tlm
       global tlm_manager
       self.counter = 1
       self.display_t = QThread()
       self.fourier_mask_cmd = ""
       self.img_data = None
       self.startup = True
       self.camera_scale_ratio = 0.50 #Set to 0.50 as an arbitrary scale that fits most cameras decently.
       self.width = 0
       self.height = 0
       self.display_mask_path = ""
       self.display_mask_file = ["", False]
       self.mask_001 = None
       self.mask_002 = None
       self.mask_003 = None

       self.spinBox_wavelength = w.subwin_fourier.findChild(QObject, "spinBox_wavelength")
       self.spinBox_prop_dist = w.subwin_fourier.findChild(QObject, "spinBox_prop_dist")
       self.button_apply = w.subwin_fourier.findChild(QObject, "button_apply")
       self.fourier_mask = w.subwin_fourier.findChild(QObject, "fourier_mask")
       self.label_source = w.subwin_fourier.findChild(QObject, "label_source")
       self.image_sample = w.subwin_fourier.findChild(QObject, 'image_sample')
       self.button_close = w.subwin_fourier.findChild(QObject, "button_close")
       self.icon_playback_status = w.subwin_fourier.findChild(QObject, "icon_playback_status")
       self.pixel_value = w.subwin_fourier.findChild(QObject, "pixel_value")
       self.label_pixelval_amnt = w.subwin_fourier.findChild(QObject, "label_pixelval_amnt")
       self.slider_performance = w.subwin_fourier.findChild(QObject, "slider_performance")
       self.slider_performance.qml_signal_send_perf_mode.connect(self.SetPerformance)
       self.button_histogram = w.subwin_fourier.findChild(QObject, "button_histogram")

       #connect signals to their appropriate slots
       self.button_apply.qml_signal_fourier_mask_cmd.connect(self.ApplyMask)
       self.button_close.qml_signal_stop_streaming.connect(self.CloseWin)
       self.pixel_value.qml_signal_mouse_pos.connect(self.SendMousePos)
       self.button_histogram.qml_signal_enable_historgram.connect(self.EnableHistogram)

       # This signal can be emitted up to three times to create a mask display for the user
       self.fourier_mask.mask_pos.connect(self.CreateDisplayMask)
       self.fourier_mask.remove_mask.connect(self.RemoveDisplayMask)

       # Connect telemetry object to slot
       # This signal will be pickup:
       #  1. start/stop
       #  2. Wavelength
       #  3. Propagation Distance
       tlm_manager.sig_callback.connect(self.UpdateTlm)
 
       # Get latest telemetry by calling "OpenWin"
       self.OpenWin()

       # Set up a new gui client
       self.display_t = guiclient(HOST,FOURIER_FRAME_PORT)
       self.display_t.start()

       OutputDebug("Fourier Window init Complete.")
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

    def CloseWin(self):
       DhmCommand("guiserver enable_fourier=false")
       w.toolbutton_display_fourier.setUnselected()


    def OpenWin(self):
       if(tlm_manager.framesource["state"] != None):
          if(tlm_manager.framesource["state"] == 1):
              self.icon_playback_status.setPlaying()
              w.run_and_idle.setSelected(1)
          if(tlm_manager.framesource["state"] == 0):
              self.icon_playback_status.setStopped()
              w.run_and_idle.setSelected(3)

       if(tlm_manager.session["num_wavelength"] != None):
          self.spinBox_wavelength.setProperty("to",tlm_manager.session["num_wavelength"])
          w.subwin_fourier.setProperty("max_wavelength",tlm_manager.session["num_wavelength"])
       if(tlm_manager.reconstruction["num_propagation_distance"] != None):
          self.spinBox_prop_dist.setProperty("to",tlm_manager.reconstruction["num_propagation_distance"])
          w.subwin_fourier.setProperty("max_prop_dist",tlm_manager.reconstruction["num_propagation_distance"])


    def UpdateTlm(self,key,value):
       if(key == "state" and value != None):
          if(tlm_manager.framesource["state"] == 1):
              self.icon_playback_status.setPlaying()
              w.run_and_idle.setSelected(1)
          if(tlm_manager.framesource["state"] == 0):
              self.icon_playback_status.setStopped()
              w.run_and_idle.setSelected(3)
       if(key == "num_wavelength" and value != None):
          self.spinBox_wavelength.setProperty("to",tlm_manager.session["num_wavelength"])
          w.subwin_fourier.setProperty("max_wavelength",tlm_manager.session["num_wavelength"])
       if(key == "num_propagation_distance" and value != None):
          self.spinBox_prop_dist.setProperty("to",tlm_manager.reconstruction["num_propagation_distance"])
          w.subwin_fourier.setProperty("max_prop_dist",tlm_manager.reconstruction["num_propagation_distance"])


    # When this is called by the main window (signal/slot), this will start a 
    # series of events which will spawn Qt threads and begin the actual playback
    def BeginPlayback(self):
       self.display_t.sig_img_complete.connect(self.UpdateImage)
       self.display_t.sig_hist_val.connect(self.UpdateHistogram)
       self.display_t.set_mode("reconst")
       self.display_t.set_win("fourier")
       self.display_t.start()


    # PYQT SLOT
    # This is a new performance feature (as of v0.8.7) that allows the user
    # to set higher performance / lower resolution / faster vs. higher quality /higher resolution / slower
    def SetPerformance(self,perf):
        self.display_t.performance_val = perf


    def RemoveDisplayMask(self, mask_no):
       if(mask_no == 1):
          self.mask_001 = None
       if(mask_no == 2):
          self.mask_002 = None
       if(mask_no == 3):
          self.mask_003 = None


    def CreateDisplayMask(self, mask_no, radius, x, y):
        self.display_mask_path = '/tmp/'
        self.performance_scalar = 4
        #print("Masking info: masking number - "+str(mask_no)+", radius - "+str(radius)+", x position -  "+str(x)+", y position - "+str(y))

        # QML will only reload a new image if the path is different since QML caches images
        # Below is an aglorithm that switches between true/false to update and create a new image
        # This new miage then updates on the QML side.
        if(self.display_mask_file[1]):
           self.display_mask_file[0] = 'DisplayMask0.png'
           self.display_mask_file[1] = False
        else:
           self.display_mask_file[0] = 'DisplayMask1.png'
           self.display_mask_file[1] = True

        # PIL Coord system: x1, y1, x2, y2
        if(mask_no == 1):
           self.mask_001 = (int((x-radius)/self.performance_scalar),\
                            int((y-radius)/self.performance_scalar),\
                            int((x+radius)/self.performance_scalar),\
                            int((y+radius)/self.performance_scalar))
        if(mask_no == 2):
           self.mask_002 = (int((x-radius)/self.performance_scalar),\
                            int((y-radius)/self.performance_scalar),\
                            int((x+radius)/self.performance_scalar),\
                            int((y+radius)/self.performance_scalar))
        if(mask_no == 3):
           self.mask_003 = (int((x-radius)/self.performance_scalar),\
                            int((y-radius)/self.performance_scalar),\
                            int((x+radius)/self.performance_scalar),\
                            int((y+radius)/self.performance_scalar))
        bg = Image.new("RGBA", (int(self.width/self.performance_scalar),int(self.height/self.performance_scalar)), (000,000,000,2))#32

        mask=Image.new('L', bg.size, color=255)
        draw=ImageDraw.Draw(mask)
        if(self.mask_001):
           draw.ellipse(self.mask_001, fill=0)
        if(self.mask_002):
           draw.ellipse(self.mask_002, fill=0)
        if(self.mask_003):
           draw.ellipse(self.mask_003, fill=0)

        bg.putalpha(mask)
        bg.save(self.display_mask_path + self.display_mask_file[0])
        self.fourier_mask.update_display_mask(self.display_mask_path + self.display_mask_file[0])

    # This function takes in the display window width and height, as well as the camera
    # source width and height and computes a scale which will fit completely in frame
    # of the display window.
    def ComputeResize(self, width, height, frame_width, frame_height):
       # Going based on width as the width is always going to be larger than the hight
       # for all n*m frames.
       self.camera_scale_ratio = frame_width / width


    #PYQT SLOT
    # Called by raw_display.py.  When an image is finished being reconstructed
    # It writes to a file and then emits a signal that is received by this function
    def UpdateImage(self,timetag,width,height):
        w.subwin_fourier.update_timetag(timetag)
        self.img_data = self.display_t.outdata_RGB
        self.image_sample.reload()

        if(self.startup):
          self.width = width
          self.height = height
          self.ComputeResize(width,\
                             height,\
                             w.subwin_fourier.property("frame_width"),\
                             w.subwin_fourier.property("frame_height"))
          self.image_sample.setProperty("width",width * self.camera_scale_ratio)
          self.image_sample.setProperty("height",height * self.camera_scale_ratio)
          w.subwin_fourier.setProperty("start_width",width * self.camera_scale_ratio)
          w.subwin_fourier.setProperty("start_height",height * self.camera_scale_ratio)
          w.subwin_fourier.setProperty("source_width", width)
          w.subwin_fourier.setProperty("source_height", height)
          w.subwin_fourier.update_zoom(self.image_sample)
          self.startup = False

    def EnableHistogram(self,enabled):
       # Explicity check for true or false, no else statement.  Don't want any accidents.
       if(enabled == True):
          self.display_t.enable_histogram = True
       if(enabled == False):
          self.display_t.enable_histogram = False


    #PYQT SLOT
    # Called by raw_display.py.  When a histogram is being constructed, this 
    # function will be called and will create a graph from 0-255 with the total
    # pixel data for each point in the graph
    def UpdateHistogram(self,iterator,amount):
        w.subwin_fourier.set_histogram_val(iterator,amount)


    # PYQT SLOT
    # This is used to obtain the x,y pixel value from of the image canvas
    def SendMousePos(self,x,y):
        zoom = w.subwin_fourier.property("zoom_f")
        pixel_val = self.display_t.get_pixel_val((int(x/zoom)-1),(int(y/zoom)-1))
        self.label_pixelval_amnt.setProperty("text", pixel_val)


    def ApplyMask(self):
        self.PackCmd()


    def SaveMask(self):
        pass
 

    def LoadMask(self):
        pass
               

    def AddCircle(self,name,x,y,radius):
        if(self.fourier_mask_cmd == ""):
            self.fourier_mask_cmd = "fouriermask mask_"+name+"=["+str(int(x))+","+str(int(y))+","+str(int(radius))+"]"
        else:
            self.fourier_mask_cmd += ",mask_"+name+"=["+str(int(x))+","+str(int(y))+","+str(int(radius))+"]"


    def PackCmd(self):
        if(self.fourier_mask.property("wavelength1") != None):
            self.AddCircle("circle_1",self.fourier_mask.property("wavelength1").property("position_x"),
                 self.fourier_mask.property("wavelength1").property("position_y"),
                 self.fourier_mask.property("wavelength1").property("r"))
      
        if(self.fourier_mask.property("wavelength2") != None):
            self.AddCircle("circle_2",self.fourier_mask.property("wavelength2").property("position_x"),
                 self.fourier_mask.property("wavelength2").property("position_y"),
                 self.fourier_mask.property("wavelength2").property("r"))
        
        if(self.fourier_mask.property("wavelength3") != None):
            self.AddCircle("circle_3",self.fourier_mask.property("wavelength3").property("position_x"),
                 self.fourier_mask.property("wavelength3").property("position_y"),
                 self.fourier_mask.property("wavelength3").property("r"))
        DhmCommand(self.fourier_mask_cmd)
        self.fourier_mask_cmd = ""






# ASSOCIATED WITH THE OBJECT -- w.subwin_phase
# Please ensure that all signals and slots to update this subwindow of MCSX are
# assocaited with that object and do not create a new Qt QML object
class PhaseWin(QObject):
    def __init__(self,tlm):
       super().__init__()
       global w
       self.tlm = tlm
       global tlm_manager
       self.counter = 1
       self.display_t = QThread()
       self.img_data = None
       self.startup = True
       self.camera_scale_ratio = 0.50 #Set to 0.50 as an arbitrary scale that fits most cameras decently.

       self.spinBox_wavelength = w.subwin_phase.findChild(QObject, "spinBox_wavelength")
       self.spinBox_prop_dist = w.subwin_phase.findChild(QObject, "spinBox_prop_dist")
       self.label_source = w.subwin_phase.findChild(QObject, "label_source")
       self.image_sample = w.subwin_phase.findChild(QObject, 'image_sample')
       self.button_close = w.subwin_phase.findChild(QObject, "button_close")
       self.icon_playback_status = w.subwin_phase.findChild(QObject, "icon_playback_status")
       self.pixel_value = w.subwin_phase.findChild(QObject, "pixel_value")
       self.label_pixelval_amnt = w.subwin_phase.findChild(QObject, "label_pixelval_amnt")
       self.slider_performance = w.subwin_phase.findChild(QObject, "slider_performance")
       self.button_histogram = w.subwin_phase.findChild(QObject, "button_histogram")

       self.spinBox_wavelength.qml_signal_set_wavelegnth.connect(self.SetWavelength)
       self.spinBox_prop_dist.qml_signal_set_prop_dist.connect(self.SetPropDistance)
       self.button_close.qml_signal_stop_streaming.connect(self.CloseWin)
       self.pixel_value.qml_signal_mouse_pos.connect(self.SendMousePos)
       self.slider_performance.qml_signal_send_perf_mode.connect(self.SetPerformance)
       self.button_histogram.qml_signal_enable_historgram.connect(self.EnableHistogram)


       # Connect telemetry object to slot
       # This signal will be pickup:
       #  1. start/stop
       #  2. Wavelength
       #  3. Propagation Distance
       tlm_manager.sig_callback.connect(self.UpdateTlm)

       # Get latest telemetry by calling "OpenWin"
       self.OpenWin()

       # Launch thread
       self.display_t = guiclient(HOST,RECONST_PHASE_FRAME_PORT)
       self.display_t.start()

       OutputDebug("Reconstruction Window init Complete.")
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


    def CloseWin(self):
       DhmCommand("guiserver enable_phase=false")
       w.toolbutton_display_phase.setUnselected()

    def OpenWin(self):
       if(tlm_manager.framesource["state"] != None):
          if(tlm_manager.framesource["state"] == 1):
              self.icon_playback_status.setPlaying()
              w.run_and_idle.setSelected(1)
          if(tlm_manager.framesource["state"] == 0):
              self.icon_playback_status.setStopped()
              w.run_and_idle.setSelected(3)

       if(tlm_manager.session["num_wavelength"] != None):
          self.spinBox_wavelength.setProperty("to",tlm_manager.session["num_wavelength"])
          w.subwin_phase.setProperty("max_wavelength",tlm_manager.session["num_wavelength"])
       if(tlm_manager.reconstruction["num_propagation_distance"] != None):
          self.spinBox_prop_dist.setProperty("to",tlm_manager.reconstruction["num_propagation_distance"])
          w.subwin_phase.setProperty("max_prop_dist",tlm_manager.reconstruction["num_propagation_distance"])


    def UpdateTlm(self,key,value):
       if(key == "state" and value != None):
          if(tlm_manager.framesource["state"] == 1):
              self.icon_playback_status.setPlaying()
              w.run_and_idle.setSelected(1)
          if(tlm_manager.framesource["state"] == 0):
              self.icon_playback_status.setStopped()
              w.run_and_idle.setSelected(3)
       if(key == "num_wavelength" and value != None):
          self.spinBox_wavelength.setProperty("to",tlm_manager.session["num_wavelength"])
          w.subwin_phase.setProperty("max_wavelength",tlm_manager.session["num_wavelength"])
       if(key == "num_propagation_distance" and value != None):
          self.spinBox_prop_dist.setProperty("to",tlm_manager.reconstruction["num_propagation_distance"])
          w.subwin_phase.setProperty("max_prop_dist",tlm_manager.reconstruction["num_propagation_distance"])



    # When this is called by the main window (signal/slot), this will start a 
    # series of events which will spawn Qt threads and begin the actual playback
    def BeginPlayback(self):
       self.display_t.sig_img_complete.connect(self.UpdateImage)
       self.display_t.sig_hist_val.connect(self.UpdateHistogram)
       self.display_t.set_mode("reconst")
       self.display_t.set_win("phase")
       self.display_t.start()
       

    # PYQT SLOT
    # This is a new performance feature (as of v0.8.7) that allows the user
    # to set higher performance / lower resolution / faster vs. higher quality /higher resolution / slower
    def SetPerformance(self,perf):
        self.display_t.performance_val = perf


    # This function takes in the display window width and height, as well as the camera
    # source width and height and computes a scale which will fit completely in frame
    # of the display window.
    def ComputeResize(self, width, height, frame_width, frame_height):
       # Going based on width as the width is always going to be larger than the hight
       # for all n*m frames.
       self.camera_scale_ratio = frame_width / width


    #PYQT SLOT
    # Called by raw_display.py.  When an image is finished being reconstructed
    # It writes to a file and then emits a signal that is received by this function
    def UpdateImage(self,timetag,width,height):
        w.subwin_phase.update_timetag(timetag)
        self.img_data = self.display_t.outdata_RGB
        self.image_sample.reload()

        if(self.startup):
          self.ComputeResize(width,\
                             height,\
                             w.subwin_phase.property("frame_width"),\
                             w.subwin_phase.property("frame_height"))
          self.image_sample.setProperty("width",width * self.camera_scale_ratio)
          self.image_sample.setProperty("height",height * self.camera_scale_ratio)
          w.subwin_phase.setProperty("start_width",width * self.camera_scale_ratio)
          w.subwin_phase.setProperty("start_height",height * self.camera_scale_ratio)
          w.subwin_phase.setProperty("source_width", width)
          w.subwin_phase.setProperty("source_height", height)
          w.subwin_phase.update_zoom(self.image_sample)
          self.startup = False

    def EnableHistogram(self,enabled):
       # Explicity check for true or false, no else statement.  Don't want any accidents.
       if(enabled == True):
          self.display_t.enable_histogram = True
       if(enabled == False):
          self.display_t.enable_histogram = False


    #PYQT SLOT
    # Called by raw_display.py.  When a histogram is being constructed, this 
    # function will be called and will create a graph from 0-255 with the total
    # pixel data for each point in the graph
    def UpdateHistogram(self,iterator,amount):
        w.subwin_phase.set_histogram_val(iterator,amount)


    # PYQT SLOT
    # This is used to obtain the x,y pixel value from of the image canvas
    def SendMousePos(self,x,y):
        zoom = w.subwin_phase.property("zoom_f")
        pixel_val = self.display_t.get_pixel_val((int(x/zoom)-1),(int(y/zoom)-1))
        self.label_pixelval_amnt.setProperty("text", pixel_val)


    def SetWavelength(self, wavelength_val):
       # the values from DHMx begin at 1 whereas fir display.py, they begin at
       # 0.  So therefore an offset has to be made of n - 1
       self.display_t.wavelength = (wavelength_val - 1)


    def SetPropDistance(self, prop_dist_val):
       # the values from DHMx begin at 1 whereas fir display.py, they begin at
       # 0.  So therefore an offset has to be made of n - 1
       self.display_t.prop_distance = (prop_dist_val - 1)







# ASSOCIATED WITH THE OBJECT -- w.subwin_amplitude
# Please ensure that all signals and slots to update this subwindow of MCSX are
# assocaited with that object and do not create a new Qt QML object
class IntensityWin(QObject):
    def __init__(self,tlm):
       super().__init__()
       global w
       self.tlm = tlm
       global tlm_manager
       self.counter = 1
       self.display_t = QThread()
       self.img_data = None
       self.startup = True
       self.camera_scale_ratio = 0.50 #Set to 0.50 as an arbitrary scale that fits most cameras decently.

       self.spinBox_wavelength = w.subwin_intensity.findChild(QObject, "spinBox_wavelength")
       self.spinBox_prop_dist = w.subwin_intensity.findChild(QObject, "spinBox_prop_dist")
       self.label_source = w.subwin_intensity.findChild(QObject, "label_source")
       self.image_sample = w.subwin_intensity.findChild(QObject, 'image_sample')
       self.button_close = w.subwin_intensity.findChild(QObject, "button_close")
       self.icon_playback_status = w.subwin_intensity.findChild(QObject, "icon_playback_status")
       self.pixel_value = w.subwin_intensity.findChild(QObject, "pixel_value")
       self.label_pixelval_amnt = w.subwin_intensity.findChild(QObject, "label_pixelval_amnt")
       self.slider_performance = w.subwin_intensity.findChild(QObject, "slider_performance")
       self.button_histogram = w.subwin_intensity.findChild(QObject, "button_histogram")

       self.spinBox_wavelength.qml_signal_set_wavelegnth.connect(self.SetWavelength)
       self.spinBox_prop_dist.qml_signal_set_prop_dist.connect(self.SetPropDistance)
       self.button_close.qml_signal_stop_streaming.connect(self.CloseWin)
       self.pixel_value.qml_signal_mouse_pos.connect(self.SendMousePos)
       self.slider_performance.qml_signal_send_perf_mode.connect(self.SetPerformance)
       self.button_histogram.qml_signal_enable_historgram.connect(self.EnableHistogram)

       # Connect telemetry object to slot
       # This signal will be pickup:
       #  1. start/stop
       #  2. Wavelength
       #  3. Propagation Distance
       tlm_manager.sig_callback.connect(self.UpdateTlm)

       # Get latest telemetry by calling "OpenWin"
       self.OpenWin()
 
       # Launch GUI thread
       self.display_t = guiclient(HOST,RECONST_INT_FRAME_PORT)
       self.display_t.start()

       OutputDebug("Intensity Window init Complete.")
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


    def CloseWin(self):
       DhmCommand("guiserver enable_intensity=false")
       w.toolbutton_display_intensity.setUnselected()


    def OpenWin(self):
       if(tlm_manager.framesource["state"] != None):
          if(tlm_manager.framesource["state"] == 1):
              self.icon_playback_status.setPlaying()
              w.run_and_idle.setSelected(1)
          if(tlm_manager.framesource["state"] == 0):
              self.icon_playback_status.setStopped()
              w.run_and_idle.setSelected(3)

       if(tlm_manager.session["num_wavelength"] != None):
          self.spinBox_wavelength.setProperty("to",tlm_manager.session["num_wavelength"])
          w.subwin_intensity.setProperty("max_wavelength",tlm_manager.session["num_wavelength"])
       if(tlm_manager.reconstruction["num_propagation_distance"] != None):
          self.spinBox_prop_dist.setProperty("to",tlm_manager.reconstruction["num_propagation_distance"])
          w.subwin_intensity.setProperty("max_prop_dist",tlm_manager.reconstruction["num_propagation_distance"])


    def UpdateTlm(self,key,value):
       if(key == "state" and value != None):
          if(tlm_manager.framesource["state"] == 1):
              self.icon_playback_status.setPlaying()
              w.run_and_idle.setSelected(1)
          if(tlm_manager.framesource["state"] == 0):
              self.icon_playback_status.setStopped()
              w.run_and_idle.setSelected(3)
       if(key == "num_wavelength" and value != None):
          self.spinBox_wavelength.setProperty("to",tlm_manager.session["num_wavelength"])
          w.subwin_intensity.setProperty("max_wavelength",tlm_manager.session["num_wavelength"])
       if(key == "num_propagation_distance" and value != None):
          self.spinBox_prop_dist.setProperty("to",tlm_manager.reconstruction["num_propagation_distance"])
          w.subwin_intensity.setProperty("max_prop_dist",tlm_manager.reconstruction["num_propagation_distance"])


    # When this is called by the main window (signal/slot), this will start a 
    # series of events which will spawn Qt threads and begin the actual playback
    def BeginPlayback(self):
       self.display_t.sig_img_complete.connect(self.UpdateImage)
       self.display_t.sig_hist_val.connect(self.UpdateHistogram)
       self.display_t.set_mode("reconst")
       self.display_t.set_win("intensity")
       self.display_t.start()


    # PYQT SLOT
    # This is a new performance feature (as of v0.8.7) that allows the user
    # to set higher performance / lower resolution / faster vs. higher quality /higher resolution / slower
    def SetPerformance(self,perf):
        self.display_t.performance_val = perf


    # This function takes in the display window width and height, as well as the camera
    # source width and height and computes a scale which will fit completely in frame
    # of the display window.
    def ComputeResize(self, width, height, frame_width, frame_height):
       # Going based on width as the width is always going to be larger than the hight
       # for all n*m frames.
       self.camera_scale_ratio = frame_width / width


    #PYQT SLOT
    # Called by raw_display.py.  When an image is finished being reconstructed
    # It writes to a file and then emits a signal that is received by this function
    def UpdateImage(self,timetag,width,height):
        w.subwin_intensity.update_timetag(timetag)
        self.img_data = self.display_t.outdata_RGB
        self.image_sample.reload()

        if(self.startup):
          self.ComputeResize(width,\
                             height,\
                             w.subwin_intensity.property("frame_width"),\
                             w.subwin_intensity.property("frame_height"))
          self.image_sample.setProperty("width",width * self.camera_scale_ratio)
          self.image_sample.setProperty("height",height * self.camera_scale_ratio)
          w.subwin_intensity.setProperty("start_width",width * self.camera_scale_ratio)
          w.subwin_intensity.setProperty("start_height",height * self.camera_scale_ratio)
          w.subwin_intensity.setProperty("source_width", width)
          w.subwin_intensity.setProperty("source_height", height)
          w.subwin_intensity.update_zoom(self.image_sample)
          self.startup = False

    def EnableHistogram(self,enabled):
       # Explicity check for true or false, no else statement.  Don't want any accidents.
       if(enabled == True):
          self.display_t.enable_histogram = True
       if(enabled == False):
          self.display_t.enable_histogram = False


    #PYQT SLOT
    # Called by raw_display.py.  When a histogram is being constructed, this 
    # function will be called and will create a graph from 0-255 with the total
    # pixel data for each point in the graph
    def UpdateHistogram(self,iterator,amount):
        w.subwin_intensity.set_histogram_val(iterator,amount)


    # PYQT SLOT
    # This is used to obtain the x,y pixel value from of the image canvas
    def SendMousePos(self,x,y):
        zoom = w.subwin_intensity.property("zoom_f")
        pixel_val = self.display_t.get_pixel_val((int(x/zoom)-1),(int(y/zoom)-1))
        self.label_pixelval_amnt.setProperty("text", pixel_val)


    def SetWavelength(self, wavelength_val):
       # the values from DHMx begin at 1 whereas fir display.py, they begin at
       # 0.  So therefore an offset has to be made of n - 1
       self.display_t.wavelength = (wavelength_val - 1)


    def SetPropDistance(self, prop_dist_val):
       # the values from DHMx begin at 1 whereas fir display.py, they begin at
       # 0.  So therefore an offset has to be made of n - 1
       self.display_t.prop_distance = (prop_dist_val - 1)







# ASSOCIATED WITH THE OBJECT -- w.subwin_amplitude
# Please ensure that all signals and slots to update this subwindow of MCSX are
# assocaited with that object and do not create a new Qt QML object
class AmplitudeWin(QObject):
    def __init__(self,tlm):
       super().__init__()
       global w
       global tlm_manager
       self.tlm = tlm
       self.counter = 1
       self.display_t = QThread()
       self.img_data = None
       self.startup = True
       self.camera_scale_ratio = 0.50 #Set to 0.50 as an arbitrary scale that fits most cameras decently.

       self.spinBox_wavelength = w.subwin_amplitude.findChild(QObject, "spinBox_wavelength")
       self.spinBox_prop_dist = w.subwin_amplitude.findChild(QObject, "spinBox_prop_dist")
       self.label_source = w.subwin_amplitude.findChild(QObject, "label_source")
       self.image_sample = w.subwin_amplitude.findChild(QObject, 'image_sample')
       self.button_close = w.subwin_amplitude.findChild(QObject, "button_close")
       self.icon_playback_status = w.subwin_amplitude.findChild(QObject, "icon_playback_status")
       self.pixel_value = w.subwin_amplitude.findChild(QObject, "pixel_value")
       self.label_pixelval_amnt = w.subwin_amplitude.findChild(QObject, "label_pixelval_amnt")
       self.slider_performance = w.subwin_amplitude.findChild(QObject, "slider_performance")
       self.button_histogram = w.subwin_amplitude.findChild(QObject, "button_histogram")

       self.spinBox_wavelength.qml_signal_set_wavelegnth.connect(self.SetWavelength)
       self.spinBox_prop_dist.qml_signal_set_prop_dist.connect(self.SetPropDistance)
       self.button_close.qml_signal_stop_streaming.connect(self.CloseWin)
       self.pixel_value.qml_signal_mouse_pos.connect(self.SendMousePos)
       self.slider_performance.qml_signal_send_perf_mode.connect(self.SetPerformance)
       self.button_histogram.qml_signal_enable_historgram.connect(self.EnableHistogram)

       # Connect telemetry object to slot
       # This signal will be pickup:
       #  1. start/stop
       #  2. Wavelength
       #  3. Propagation Distance
       tlm_manager.sig_callback.connect(self.UpdateTlm)

       # Get latest telemetry by calling "OpenWin"
       self.OpenWin()

       # Launch GUI thread
       self.display_t = guiclient(HOST,RECONST_AMP_FRAME_PORT)
       self.display_t.start()

       OutputDebug("Reconstruction Window init Complete.")
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
       

    def CloseWin(self):
       DhmCommand("guiserver enable_amplitude=false")
       w.toolbutton_display_amplitude.setUnselected()


    def OpenWin(self):
       if(tlm_manager.framesource["state"] != None):
          if(tlm_manager.framesource["state"] == 1):
              self.icon_playback_status.setPlaying()
              w.run_and_idle.setSelected(1)
          if(tlm_manager.framesource["state"] == 0):
              self.icon_playback_status.setStopped()
              w.run_and_idle.setSelected(3)

       if(tlm_manager.session["num_wavelength"] != None):
          self.spinBox_wavelength.setProperty("to",tlm_manager.session["num_wavelength"])
          w.subwin_amplitude.setProperty("max_wavelength",tlm_manager.session["num_wavelength"])
       if(tlm_manager.reconstruction["num_propagation_distance"] != None):
          self.spinBox_prop_dist.setProperty("to",tlm_manager.reconstruction["num_propagation_distance"])
          w.subwin_amplitude.setProperty("max_prop_dist",tlm_manager.reconstruction["num_propagation_distance"])


    def UpdateTlm(self,key,value):
       if(key == "state" and value != None):
          if(tlm_manager.framesource["state"] == 1):
              self.icon_playback_status.setPlaying()
              w.run_and_idle.setSelected(1)
          if(tlm_manager.framesource["state"] == 0):
              self.icon_playback_status.setStopped()
              w.run_and_idle.setSelected(3)
       if(key == "num_wavelength" and value != None):
          self.spinBox_wavelength.setProperty("to",tlm_manager.session["num_wavelength"])
          w.subwin_amplitude.setProperty("max_wavelength",tlm_manager.session["num_wavelength"])
       if(key == "num_propagation_distance" and value != None):
          self.spinBox_prop_dist.setProperty("to",tlm_manager.reconstruction["num_propagation_distance"])
          w.subwin_amplitude.setProperty("max_prop_dist",tlm_manager.reconstruction["num_propagation_distance"])



    # When this is called by the main window (signal/slot), this will start a 
    # series of events which will spawn Qt threads and begin the actual playback
    def BeginPlayback(self):
       self.display_t.sig_img_complete.connect(self.UpdateImage)
       self.display_t.sig_hist_val.connect(self.UpdateHistogram)
       self.display_t.set_mode("reconst")
       self.display_t.set_win("amplitude")
       self.display_t.start()


    # PYQT SLOT
    # This is a new performance feature (as of v0.8.7) that allows the user
    # to set higher performance / lower resolution / faster vs. higher quality /higher resolution / slower
    def SetPerformance(self,perf):
        self.display_t.performance_val = perf


    # This function takes in the display window width and height, as well as the camera
    # source width and height and computes a scale which will fit completely in frame
    # of the display window.
    def ComputeResize(self, width, height, frame_width, frame_height):
       # Going based on width as the width is always going to be larger than the hight
       # for all n*m frames.
       self.camera_scale_ratio = frame_width / width


    #PYQT SLOT
    # Called by raw_display.py.  When an image is finished being reconstructed
    # It writes to a file and then emits a signal that is received by this function
    def UpdateImage(self,timetag,width,height):
        w.subwin_amplitude.update_timetag(timetag)
        self.img_data = self.display_t.outdata_RGB
        self.image_sample.reload()

        if(self.startup):
          self.ComputeResize(width,\
                             height,\
                             w.subwin_amplitude.property("frame_width"),\
                             w.subwin_amplitude.property("frame_height"))
          self.image_sample.setProperty("width",width * self.camera_scale_ratio)
          self.image_sample.setProperty("height",height * self.camera_scale_ratio)
          w.subwin_amplitude.setProperty("start_width",width * self.camera_scale_ratio)
          w.subwin_amplitude.setProperty("start_height",height * self.camera_scale_ratio)
          w.subwin_amplitude.setProperty("source_width", width)
          w.subwin_amplitude.setProperty("source_height", height)
          w.subwin_amplitude.update_zoom(self.image_sample)
          self.startup = False

    def EnableHistogram(self,enabled):
       # Explicity check for true or false, no else statement.  Don't want any accidents.
       if(enabled == True):
          self.display_t.enable_histogram = True
       if(enabled == False):
          self.display_t.enable_histogram = False


    #PYQT SLOT
    # Called by raw_display.py.  When a histogram is being constructed, this 
    # function will be called and will create a graph from 0-255 with the total
    # pixel data for each point in the graph
    def UpdateHistogram(self,iterator,amount):
        w.subwin_amplitude.set_histogram_val(iterator,amount)


    # PYQT SLOT
    # This is used to obtain the x,y pixel value from of the image canvas
    def SendMousePos(self,x,y):
        zoom = w.subwin_amplitude.property("zoom_f")
        pixel_val = self.display_t.get_pixel_val((int(x/zoom)-1),(int(y/zoom)-1))
        self.label_pixelval_amnt.setProperty("text", pixel_val)


    def SetWavelength(self, wavelength_val):
       # the values from DHMx begin at 1 whereas fir display.py, they begin at
       # 0.  So therefore an offset has to be made of n - 1.
       self.display_t.wavelength = (wavelength_val - 1)


    def SetPropDistance(self, prop_dist_val):
       # the values from DHMx begin at 1 whereas fir display.py, they begin at
       # 0.  So therefore an offset has to be made of n - 1
       self.display_t.prop_distance = (prop_dist_val - 1)







# ASSOCIATED WITH THE OBJECT -- w.subwin_holo_display
# Please ensure that all signals and slots to update this subwindow of MCSX are
# assocaited with that object and do not create a new Qt QML object
class HologramWin(QObject):
    def __init__(self,tlm):
       super().__init__()
       global w
       global tlm_manager
       self.tlm = tlm
       self.counter = 1
       self.display_t = QThread()
       self.img_data = None
       self.startup = True
       self.camera_scale_ratio = 0.50 #Set to 0.50 as an arbitrary scale that fits most cameras decently.

       self.label_source = w.subwin_holo_display.findChild(QObject, "label_source")
       self.image_sample = w.subwin_holo_display.findChild(QObject, "image_sample")
       self.canvas_area = w.subwin_holo_display.findChild(QObject, "canvas_area")
       self.sample_area = w.subwin_holo_display.findChild(QObject,"sample_area")
       self.button_close = w.subwin_holo_display.findChild(QObject, "button_close")
       self.icon_playback_status = w.subwin_holo_display.findChild(QObject, "icon_playback_status")
       self.pixel_value = w.subwin_holo_display.findChild(QObject, "pixel_value")
       self.label_pixelval_amnt = w.subwin_holo_display.findChild(QObject, "label_pixelval_amnt")
       self.slider_performance = w.subwin_holo_display.findChild(QObject, "slider_performance")
       self.button_histogram = w.subwin_holo_display.findChild(QObject, "button_histogram")

       self.button_close.qml_signal_stop_streaming.connect(self.CloseWin)
       self.pixel_value.qml_signal_mouse_pos.connect(self.SendMousePos)
       self.slider_performance.qml_signal_send_perf_mode.connect(self.SetPerformance)
       self.button_histogram.qml_signal_enable_historgram.connect(self.EnableHistogram)

       # Connect telemetry object to slot
       # In the telemetry manager below, all that the hologram window is concerned with
       # is the playback status of whether or not the hologram is getting data from a source
       tlm_manager.sig_callback.connect(self.UpdateTlm)

       # Get latest telemetry by calling "OpenWin"
       self.OpenWin()

       # Launch GUI thread
       self.display_t = guiclient(HOST,RAW_FRAME_PORT)
       self.display_t.start()

       OutputDebug("Hologram Window init Complete.")
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


    def CloseWin(self):
       DhmCommand("guiserver enable_rawframes=false")
       w.toolbutton_display_hologram.setUnselected()

    def OpenWin(self):
       if(tlm_manager.framesource["state"] != None):
          if(tlm_manager.framesource["state"] == 1):
              self.icon_playback_status.setPlaying()
              w.run_and_idle.setSelected(1)
          if(tlm_manager.framesource["state"] == 0):
              self.icon_playback_status.setStopped()
              w.run_and_idle.setSelected(3)


    def UpdateTlm(self,key,value):
       if(key == "state"):
          if(tlm_manager.framesource["state"] == 1):
              self.icon_playback_status.setPlaying()
              w.run_and_idle.setSelected(1)
          if(tlm_manager.framesource["state"] == 0):
              self.icon_playback_status.setStopped()
              w.run_and_idle.setSelected(3)


    # PYQT SLOT
    # This is a new performance feature (as of v0.8.7) that allows the user
    # to set higher performance / lower resolution / faster vs. higher quality /higher resolution / slower
    def SetPerformance(self,perf):
        self.display_t.performance_val = perf


    # PYQT SLOT
    # This is used to obtain the x,y pixel value from of the image canvas
    # NOTE: display.py the x,y values are flipped. so x==y, y==x in display.py
    # TODO: Fix the x,y flip.
    def SendMousePos(self,x,y):
        zoom = w.subwin_holo_display.property("zoom_f")
        pixel_val = self.display_t.get_pixel_val((int(x/zoom)-1),(int(y/zoom)-1))
        self.label_pixelval_amnt.setProperty("text", pixel_val)


    # When this is called by the main window (signal/slot), this will start a 
    # series of events which will spawn Qt threads and begin the actual playback
    def BeginPlayback(self):
       self.display_t.sig_img_complete.connect(self.UpdateImage)
       self.display_t.sig_hist_val.connect(self.UpdateHistogram)
       self.display_t.set_win("raw")
       self.display_t.start()


    # This function takes in the display window width and height, as well as the camera
    # source width and height and computes a scale which will fit completely in frame
    # of the display window.
    def ComputeResize(self, width, height, frame_width, frame_height):
       # Going based on width as the width is always going to be larger than the hight
       # for all n*m frames.
       self.camera_scale_ratio = frame_width / width


    #PYQT SLOT
    # Called by raw_display.py.  When an image is finished being reconstructed
    # It writes to a file and then emits a signal that is received by this function
    def UpdateImage(self,timetag,width,height):
        w.subwin_holo_display.update_timetag(timetag)
        self.img_data = self.display_t.outdata_RGB
        self.image_sample.reload()

        if(self.startup): 
          self.ComputeResize(width,\
                             height,\
                             w.subwin_holo_display.property("frame_width"),\
                             w.subwin_holo_display.property("frame_height"))
          print("frame size: "+str(width)+"x"+str(height))
          print("Scaled frame size: "+str(width * self.camera_scale_ratio)+"x"+str(height * self.camera_scale_ratio))
          self.image_sample.setProperty("width",width * self.camera_scale_ratio)
          self.image_sample.setProperty("height",height * self.camera_scale_ratio)
          w.subwin_holo_display.setProperty("start_width",width * self.camera_scale_ratio)
          w.subwin_holo_display.setProperty("start_height",height * self.camera_scale_ratio)
          w.subwin_holo_display.setProperty("source_width", width)
          w.subwin_holo_display.setProperty("source_height", height)
          w.subwin_holo_display.update_zoom(self.image_sample)
          self.startup = False



    def EnableHistogram(self,enabled):
       # Explicity check for true or false, no else statement.  Don't want any accidents.
       if(enabled == True):
          self.display_t.enable_histogram = True
       if(enabled == False):
          self.display_t.enable_histogram = False


    #PYQT SLOT
    # Called by raw_display.py.  When a histogram is being constructed, this 
    # function will be called and will create a graph from 0-255 with the total
    # pixel data for each point in the graph
    def UpdateHistogram(self,iterator,amount):
         w.subwin_holo_display.set_histogram_val(iterator,amount)
   





class ConfigurationWin(QObject):
    def __init__(self,tlm):
      super().__init__()
      global w
      global wl_and_prop
      global tlm_manager
      self.tlm = tlm
      self.conf_open_flag = False
      self.cfg_file = ""

      #Accessible wavelength amount
      self.num_wavelength = 0

      # Get window objects so that python can manipulate its properties with the received tlm
      self.textField_session_name = w.subwin_conf.findChild(QObject, 'textField_session_name')
      self.textArea_desc = w.subwin_conf.findChild(QObject, 'textArea_desc')
      self.radio_t1_mono = w.subwin_conf.findChild(QObject, 'radio_t1_mono')
      self.radio_t1_multi = w.subwin_conf.findChild(QObject, 'radio_t1_multi')
      self.spinBox_t2_crop = w.subwin_conf.findChild(QObject, 'spinBox_t2_crop')
      self.spinBox_t2_rebin = w.subwin_conf.findChild(QObject, 'spinBox_t2_rebin')
      self.spinBox_t3_width = w.subwin_conf.findChild(QObject, "spinBox_t3_width")
      self.spinBox_t3_height = w.subwin_conf.findChild(QObject, "spinBox_t3_height")
      self.spinBox_t3_dx = w.subwin_conf.findChild(QObject, 'spinBox_t3_dx')
      self.spinBox_t3_dy = w.subwin_conf.findChild(QObject, 'spinBox_t3_dy')
      self.spinBox_t4_focal = w.subwin_conf.findChild(QObject, 'spinBox_t4_focal')
      self.spinBox_t4_num_ap = w.subwin_conf.findChild(QObject, 'spinBox_t4_num_ap')
      self.spinBox_t4_sys_mag = w.subwin_conf.findChild(QObject, 'spinBox_t4_sys_mag')
      self.combo_t1_w1 = w.subwin_conf.findChild(QObject, 'combo_t1_w1')
      self.combo_t1_w2 = w.subwin_conf.findChild(QObject, 'combo_t1_w2')
      self.combo_t1_w3 = w.subwin_conf.findChild(QObject, 'combo_t1_w3')
      self.button_close = w.subwin_conf.findChild(QObject, 'button_close')
      self.button_load = w.subwin_conf.findChild(QObject, 'button_load')
      self.button_save = w.subwin_conf.findChild(QObject, 'button_save')

      # Session Defaults - initialize to null/None for now
      # The session defaults will be read in once the first telemetry packet
      # is received.
      self.textField_session_name_default = None
      self.textArea_desc_default = None
      self.radio_t1_mono_default = None
      self.radio_t1_multi_default = None
      self.spinBox_t2_crop_default = None
      self.spinBox_t2_rebin_default = None
      self.spinBox_t3_width_default = None
      self.spinBox_t3_height_default = None
      self.spinBox_t3_dx_default = None
      self.spinBox_t3_dy_default = None
      self.spinBox_t4_focal_default = None
      self.spinBox_t4_num_ap_default = None
      self.spinBox_t4_sys_mag_default = None
      self.combo_t1_w1_default = None
      self.combo_t1_w2_default = None
      self.combo_t1_w3_default = None

      # connect signals directly to slots via lambda 
      w.subwin_conf.pack_cmd.connect(self.SendCommand)
      self.tlm.DhmxTlm.tlm_data_session.connect(self.UpdateTlm)
      self.button_close.qml_signal_close.connect(self.CloseWin)
      self.button_load.clicked.connect(self.LoadCfgFile)
      self.button_save.clicked.connect(self.SaveCfgFile)
      
      OutputDebug("Configuration Window created")


    def CloseWin(self):
       w.toolbutton_new_session.setUnselected()

    def SaveCfgFile(self):
       # Call reconst to ensure that all values are updated properly and written to the config file string
       self.SetTlmMode(True)
       DhmCommand("session")
       self.UpdateConfigFile()

       # Launch save window and write to file
       SaveFile("ses",self.cfg_file, int(w.subwin_conf.property("x"))+int((w.subwin_conf.property("width")/2)), \
            int(w.subwin_conf.property("y"))+ int((w.subwin_conf.property("height")/2)),\
            "/home","Save Session File")

       
    def LoadCfgFile(self):
       cfg = LoadFile("ses",int(w.subwin_conf.property("x"))+int((w.subwin_conf.property("width")/2)), \
               int(w.subwin_conf.property("y"))+ int((w.subwin_conf.property("height")/2)),\
               "/home","Load Session File")
       DhmCommand(cfg)
       self.SetTlmMode(True)
       DhmCommand("session")

    
    def UpdateConfigFile(self):
         self.cfg_file = w.subwin_conf.get_session_cfg()


    def SetTlmMode(self,decision):
       self.conf_open_flag = decision


    def GetTlmMode(self):
       return self.conf_open_flag


    def SendCommand(self,cmd):
        DhmCommand(cmd)


    def GetWavelength(self, input_thing):
        return int(input_thing * 10e+8)


    def GetNumOfWavelength(self):
        return self.num_wavelength


    def UpdateTlm(self,tlm_data):
      if(self.GetTlmMode() == True):
         tlm_manager.session['name'] = tlm_data.name.split(b'\0',1)[0].decode('ASCII')
         tlm_manager.session['description'] = tlm_data.description.split(b'\0',1)[0].decode('ASCII')

         self.textField_session_name.setProperty("text",tlm_manager.session['name'].strip())
         self.textField_session_name_default = self.textField_session_name

         self.textArea_desc.setProperty("text",tlm_manager.session['description'].strip())
         self.textArea_desc_default = self.textArea_desc
         
         if(tlm_data.num_wavelength == 1):
            self.radio_t1_mono.setProperty("checked",True)
            self.radio_t1_multi.setProperty("checked",False)
         else:
            self.radio_t1_mono.setProperty("checked",False)
            self.radio_t1_multi.setProperty("checked",True)

         self.radio_t1_mono_default = self.radio_t1_mono
         self.radio_t1_multi_default = self.radio_t1_multi

         tlm_manager.session["num_wavelength"] = tlm_data.num_wavelength
         self.num_wavelength_default = tlm_manager.session["num_wavelength"]

         tlm_manager.session["wavelength_1"] = self.GetWavelength(tlm_data.wavelength[0])
         if(tlm_manager.session["wavelength_1"] == 405):
            self.combo_t1_w1.setProperty("currentIndex",0)
         if(tlm_manager.session["wavelength_1"] == 488):
            self.combo_t1_w1.setProperty("currentIndex",1)
         if(tlm_manager.session["wavelength_1"] == 532):
            self.combo_t1_w1.setProperty("currentIndex",2)    

         self.combo_t1_w1_default =  self.combo_t1_w1
     
         tlm_manager.session["wavelength_2"] = self.GetWavelength(tlm_data.wavelength[1])
         if(tlm_manager.session["wavelength_2"] == 405):
            self.combo_t1_w2.setProperty("currentIndex",0)
         if(tlm_manager.session["wavelength_2"] == 488):
            self.combo_t1_w2.setProperty("currentIndex",1)
         if(tlm_manager.session["wavelength_2"] == 532):
            self.combo_t1_w2.setProperty("currentIndex",2) 

         self.combo_t1_w2_default =  self.combo_t1_w2

         tlm_manager.session["wavelength_3"] = self.GetWavelength(tlm_data.wavelength[2])
         if(tlm_manager.session["wavelength_3"] == 405):
            self.combo_t1_w3.setProperty("currentIndex",0)
         if(tlm_manager.session["wavelength_3"] == 488):
            self.combo_t1_w3.setProperty("currentIndex",1)
         if(tlm_manager.session["wavelength_3"] == 532):
            self.combo_t1_w3.setProperty("currentIndex",2) 

         self.combo_t1_w3_default =  self.combo_t1_w3

         #TODO: Future TLM may have width/height
         #self.spinBox_t3_width.setProperty("value",tlm_data.width)
         #self.spinBox_t3_width.setProperty("value",tlm_data.height)
         tlm_manager.session["crop_fraction"] = tlm_data.crop_fraction
         self.spinBox_t2_crop.setProperty("value",tlm_manager.session["crop_fraction"])
         self.spinBox_t2_crop_default = self.spinBox_t2_crop

         tlm_manager.session['rebin_factor'] = tlm_data.rebin_factor
         self.spinBox_t2_rebin.setProperty("value",tlm_manager.session['rebin_factor'])
         self.spinBox_t2_rebin_default = self.spinBox_t2_rebin

         tlm_manager.session['dx'] = w.subwin_conf.metric_conversion((tlm_data.dx),"m","um")
         self.spinBox_t3_dx.setProperty("realValue",tlm_manager.session['dx'])
         self.spinBox_t3_dx_default = self.spinBox_t3_dx

         tlm_manager.session['dy'] = w.subwin_conf.metric_conversion((tlm_data.dy),"m","um")
         self.spinBox_t3_dy.setProperty("realValue",tlm_manager.session['dy'])
         self.spinBox_t3_dy_default = self.spinBox_t3_dy

         tlm_manager.session['focal_length'] = w.subwin_conf.metric_conversion((tlm_data.lens_focal_length),"m","mm")
         self.spinBox_t4_focal.setProperty("realValue",tlm_manager.session['focal_length'])
         self.spinBox_t4_focal_default = self.spinBox_t4_focal

         tlm_manager.session['numerical_aperture'] = w.subwin_conf.metric_conversion((tlm_data.lens_numerical_aperture),"m","mm")
         self.spinBox_t4_num_ap.setProperty("realValue",tlm_manager.session['numerical_aperture'])
         self.spinBox_t4_num_ap_default = self.spinBox_t4_num_ap

         tlm_manager.session['lens_system_magnification'] = w.subwin_conf.metric_conversion((tlm_data.lens_system_magnification),"m","mm")
         self.spinBox_t4_sys_mag.setProperty("realValue",tlm_manager.session['lens_system_magnification'])
         self.spinBox_t4_sys_mag_default = self.spinBox_t4_sys_mag

         self.SetTlmMode(False)

      # And output status messages to the DHMX debug output --
      tlm_manager.session['status'] = tlm_data.status_msg.decode('ASCII')
      OutputDebug("Telemetry: Session Window - "+tlm_manager.session['status'])






class ReconstructionWin(QObject):

    def __init__(self,tlm):
      super().__init__()
      global w
      global wl_and_prop
      global tlm_manager
      self.recon_open_flag = False
      self.tlm = tlm
      self.num_wavelength = 0
      self.cfg_file = ""

      # Get window objects so that python can manipulate its properties with the received tlm
      self.spinBox_num_dist = w.subwin_recon.findChild(QObject, 'spinBox_num_dist')  
      self.spinBox_prop_1 = w.subwin_recon.findChild(QObject, 'spinBox_prop_1')
      self.spinBox_prop_2 = w.subwin_recon.findChild(QObject, 'spinBox_prop_2')
      self.spinBox_prop_3 = w.subwin_recon.findChild(QObject, 'spinBox_prop_3')  
      self.slider_prop_1 = w.subwin_recon.findChild(QObject, 'slider_prop_1')
      self.slider_prop_2 = w.subwin_recon.findChild(QObject, 'slider_prop_2')
      self.slider_prop_3 = w.subwin_recon.findChild(QObject, 'slider_prop_3')
      self.spinBox_chrom_shift_1 = w.subwin_recon.findChild(QObject, 'spinBox_chrom_shift_1')
      self.spinBox_chrom_shift_2 = w.subwin_recon.findChild(QObject, 'spinBox_chrom_shift_2')  
      self.radio_t1_1d_seg = w.subwin_recon.findChild(QObject, 'radio_t1_1d_seg')
      self.radio_t1_2d_seg = w.subwin_recon.findChild(QObject, 'radio_t1_2d_seg')
      self.check_t2_use_ref = w.subwin_recon.findChild(QObject,'check_t2_use_ref')
      self.textField_holo = w.subwin_recon.findChild(QObject, 'textField_holo')
      self.spinBox_t2_avg = w.subwin_recon.findChild(QObject, 'spinBox_t2_avg')
      self.check_t2_avg = w.subwin_recon.findChild(QObject, 'check_t2_avg')
      self.spinBox_t3_offset_x = w.subwin_recon.findChild(QObject, 'spinBox_t3_offset_x')
      self.spinBox_t3_offset_y = w.subwin_recon.findChild(QObject, 'spinBox_t3_offset_y')
      self.spinBox_t3_size_x = w.subwin_recon.findChild(QObject, 'spinBox_t3_size_x')
      self.spinBox_t3_size_y = w.subwin_recon.findChild(QObject, 'spinBox_t3_size_y')
      self.check_t4_unwrap = w.subwin_recon.findChild(QObject, 'check_t4_unwrap')
      self.comboBox_t4_alg = w.subwin_recon.findChild(QObject, 'comboBox_t4_alg')
      self.button_t1_center = w.subwin_recon.findChild(QObject, 'button_t1_center')
      self.button_t1_center_tilt = w.subwin_recon.findChild(QObject, 'button_t1_center_tilt')
      self.radio_t1_max_val = w.subwin_recon.findChild(QObject, 'radio_t1_max_val')
      self.radio_t1_wide_spec = w.subwin_recon.findChild(QObject, 'radio_t1_wide_spec')
      self.slider_chrom_shift_1 = w.subwin_recon.findChild(QObject, 'slider_chrom_shift_1')
      self.slider_chrom_shift_2 = w.subwin_recon.findChild(QObject, 'slider_chrom_shift_2')
      self.button_undo = w.subwin_recon.findChild(QObject, 'button_undo')
      self.button_save = w.subwin_recon.findChild(QObject, 'button_save')
      self.button_load = w.subwin_recon.findChild(QObject, 'button_load')


      

      # Reconst Defaults - initialize to null/None for now
      # The Reconst defaults will be read in once the first telemetry packet
      # is received.
      self.num_propagation_distance = None
      self.propagation_distance = [None,None,None,]
      self.compute_spectral_peak = None
      self.compute_digital_phase_mask = None
      self.processing_mode = None
      self.num_chromatic_shift = None 
      self.chromatic_shift = [None,None,None,] 
      self.one_d_segment = None
      self.two_d_segment = None
      self.max_val = None
      self.wide_spec = None
      self.center_image = None
      self.center_tilt = None
      self.ref_holo_path = None 
      self.ref_holo_enable = None 
      self.ref_holo_averaging_sec = None 
      self.ref_holo_averaging_enabled = None 
      self.phase_unwrapping_enabled = None
      self.phase_unwrapping_algorithm = None 
      self.fitting_mode = None
      self.fitting_method = None
      self.fitting_order = None
      self.fitting_apply = None
      self.reset_phase_mask = None
      self.roi_offset_x = None
      self.roi_offset_y = None
      self.roi_size_x = None
      self.roi_size_y = None
      self.store_files = None 
      self.center_image = None 
      self.center_image_and_tilt = None
      self.center_max_value = None 
      self.center_wide_spectrum = None 
      self.status_msg = None 
      
      self.set_defaults = True

      # connect signals directly to slots via lambda 
      w.subwin_recon.pack_cmd.connect(self.SendCommand)
      self.button_undo.qml_signal_undo.connect(self.RevertChanges)
      self.tlm.DhmxTlm.tlm_data_reconst.connect(self.UpdateTlm)
      self.button_save.clicked.connect(self.SaveCfgFile)
      self.button_load.clicked.connect(self.LoadCfgFile)
      # Call session telemetry to get the number of wavelengths needed
      tlm_manager.sig_callback.connect(self.UpdateWavelength)
      DhmCommand("session")
      
      # Set telemetry receiving to be valid and ask for reconstruction telemetry
      self.SetTlmMode(True)
      DhmCommand("reconst")
      OutputDebug("Reconstruction Window created")




    def Show(self):
       self.set_defaults = True
       self.SetTlmMode(True)
       DhmCommand("reconst")



    def SaveCfgFile(self):
       # Call reconst to ensure that all values are updated properly and written to the config file string
       self.SetTlmMode(True)
       DhmCommand("reconst")
       self.UpdateConfigFile()

       # Launch save window and write to file
       SaveFile("cfg",self.cfg_file, int(w.subwin_recon.property("x"))+int((w.subwin_recon.property("width")/2)), \
            int(w.subwin_recon.property("y"))+ int((w.subwin_recon.property("height")/2)),\
            "/home","Save Configuration File")

       
    def LoadCfgFile(self):
       cfg = LoadFile("cfg",int(w.subwin_recon.property("x"))+int((w.subwin_recon.property("width")/2)), \
               int(w.subwin_recon.property("y"))+ int((w.subwin_recon.property("height")/2)),\
               "/home","Load Configuration File")
       DhmCommand(cfg)
       self.SetTlmMode(True)
       DhmCommand("reconst")


    def UpdateConfigFile(self):
        # Update Command String to be used as the cfg file
        #self.cfg_file = ("reconst num_propagation_distance="+str(self.spinBox_num_dist.property("value"))+"\n,"+
        self.cfg_file= ("reconst propagation_distance=["+str(self.spinBox_prop_1.property("realValue"))+\
               ","+str(self.spinBox_prop_2.property("realValue"))+\
               ","+str(self.spinBox_prop_3.property("realValue"))+"]\n,"+ 
           #"num_chromatic_shift="+str()+"\n,"+
           "chromatic_shift=["+str(self.spinBox_chrom_shift_1.property("realValue"))+","+str(self.spinBox_chrom_shift_2.property("realValue"))+"]\n,"+  
           #"fitting_mode="+str()+"\n,"+
           #"fitting_order="+str()+"\n,"+
           "roi_offset_x="+str(self.spinBox_t3_offset_x.property("value"))+"\n,"+
           "roi_offset_y="+str(self.spinBox_t3_offset_y.property("value"))+"\n,"+
           "roi_size_x="+str(self.spinBox_t3_size_x.property("value"))+"\n,"+
           "roi_size_y="+str(self.spinBox_t3_size_y.property("value")).lower()+", "+
           "center_image="+str(self.button_t1_center.property("checked")).lower()+", "+
           "center_image_and_tilt="+str(self.button_t1_center_tilt.property("checked")).lower()+", "+
           "center_max_value="+str(self.radio_t1_max_val.property("checked")).lower()+", "+
           "center_wide_spectrum="+str(self.radio_t1_wide_spec.property("checked")).lower())
           #"ref_holo_enable="+str()+"\n,"+
           #"ref_holo_averaging_sec="+str()+"\n,"+
           #"phase_unwrapping_enable="+str())


    def SetTlmMode(self,decision):
       self.recon_open_flag = decision


    def GetTlmMode(self):
       return self.recon_open_flag


    def SendCommand(self,cmd):
        DhmCommand(cmd)


    def UpdateWavelength(self,key, value):
        if(key == "num_wavelength"):
           self.num_wavelength = value

           if(self.num_wavelength == 1):
              self.spinBox_chrom_shift_1.setProperty("enabled",False)
              self.spinBox_chrom_shift_2.setProperty("enabled",False)
              self.slider_chrom_shift_1.setProperty("enabled",False)
              self.slider_chrom_shift_2.setProperty("enabled",False)

           if(self.num_wavelength == 2):
              self.spinBox_chrom_shift_1.setProperty("enabled",True)
              self.spinBox_chrom_shift_2.setProperty("enabled",False)
              self.slider_chrom_shift_1.setProperty("enabled",True)
              self.slider_chrom_shift_2.setProperty("enabled",False)

           if(self.num_wavelength == 3):
              self.spinBox_chrom_shift_1.setProperty("enabled",True)
              self.spinBox_chrom_shift_2.setProperty("enabled",True)
              self.slider_chrom_shift_1.setProperty("enabled",True)
              self.slider_chrom_shift_2.setProperty("enabled",True)

        #self.num_wavelength = tlm_data.num_wavelength
        #wl_and_prop.SetMaxWl(tlm_data.num_wavelength)



    def UpdateTlm(self,tlm_data):
        if(self.GetTlmMode() == True):
           OutputDebug("Updating Window Telemetry...")

           # Propagation Distances
           tlm_manager.reconstruction["num_propagation_distance"] = tlm_data.num_propagation_distance
           self.spinBox_num_dist.setProperty("value",tlm_manager.reconstruction["num_propagation_distance"])
           tlm_manager.reconstruction["propagation_distance_1"] = tlm_data.propagation_distance[0]
           tlm_manager.reconstruction["propagation_distance_2"] = tlm_data.propagation_distance[1]
           tlm_manager.reconstruction["propagation_distance_3"] = tlm_data.propagation_distance[2]
           self.spinBox_prop_1.setProperty("realValue",tlm_manager.reconstruction["propagation_distance_1"])
           self.spinBox_prop_2.setProperty("realValue",tlm_manager.reconstruction["propagation_distance_2"])
           self.spinBox_prop_3.setProperty("realValue",tlm_manager.reconstruction["propagation_distance_3"])

           self.slider_prop_1.setProperty("value",tlm_manager.reconstruction["propagation_distance_1"])
           self.slider_prop_2.setProperty("value",tlm_manager.reconstruction["propagation_distance_2"])
           self.slider_prop_3.setProperty("value",tlm_manager.reconstruction["propagation_distance_3"]) 

           # Chromatic Shifts
           # Need to send a session command to get number of wavelengths as tlm
           # All chromatic shifts are N-1.  Where N is the number of wavelengths
           if(self.num_wavelength == 1):
              self.spinBox_chrom_shift_1.setProperty("enabled",False)
              self.spinBox_chrom_shift_2.setProperty("enabled",False)
              self.slider_chrom_shift_1.setProperty("enabled",False)
              self.slider_chrom_shift_2.setProperty("enabled",False)
           if(self.num_wavelength == 2):
              self.spinBox_chrom_shift_1.setProperty("enabled",True)
              self.spinBox_chrom_shift_2.setProperty("enabled",False)
              self.slider_chrom_shift_1.setProperty("enabled",True)
              self.slider_chrom_shift_2.setProperty("enabled",False)
           if(self.num_wavelength == 3):
              self.spinBox_chrom_shift_1.setProperty("enabled",True)
              self.spinBox_chrom_shift_2.setProperty("enabled",True)
              self.slider_chrom_shift_1.setProperty("enabled",True)
              self.slider_chrom_shift_2.setProperty("enabled",True)
           tlm_manager.reconstruction["num_chromatic_shift"] = tlm_data.num_chromatic_shift
           tlm_manager.reconstruction["chromatic_shift_1"] = tlm_data.chromatic_shift[0]
           tlm_manager.reconstruction["chromatic_shift_2"] = tlm_data.chromatic_shift[1]
           self.spinBox_chrom_shift_1.setProperty("value",tlm_manager.reconstruction["chromatic_shift_1"])
           self.spinBox_chrom_shift_2.setProperty("value",tlm_manager.reconstruction["chromatic_shift_2"]) 

           # Enable Reference Hologram
           tlm_manager.reconstruction["ref_holo_enable"] = tlm_data.ref_holo_enable           
           self.check_t2_use_ref.setProperty("checked",tlm_manager.reconstruction["ref_holo_enable"])

           # Reference Hologram Path
           tlm_manager.reconstruction["ref_holo_path"] = tlm_data.ref_holo_path
           self.textField_holo.setProperty("text",tlm_data.ref_holo_path)

           # Reference Hologram Averaging in Seconds
           tlm_manager.reconstruction["ref_holo_averaging_sec"] = tlm_data.ref_holo_averaging_sec
           self.spinBox_t2_avg.setProperty("value",tlm_manager.reconstruction["ref_holo_averaging_sec"])

           # Enable Hologram Averaging
           tlm_manager.reconstruction["ref_holo_averaging_enabled"] = tlm_data.ref_holo_averaging_enabled
           self.check_t2_avg.setProperty("checked",tlm_manager.reconstruction["ref_holo_averaging_enabled"])

           # Region of interest offset X and Y
           tlm_manager.reconstruction["roi_offset_x"] = tlm_data.roi_offset_x
           tlm_manager.reconstruction["roi_offset_y"] = tlm_data.roi_offset_y
           self.spinBox_t3_offset_x.setProperty("value", tlm_manager.reconstruction["roi_offset_x"])
           self.spinBox_t3_offset_y.setProperty("value", tlm_manager.reconstruction["roi_offset_y"])

           # Region of interestg size X and Y
           tlm_manager.reconstruction["roi_size_x"] = tlm_data.roi_size_x
           tlm_manager.reconstruction["roi_size_y"] = tlm_data.roi_size_y
           self.spinBox_t3_size_x.setProperty("value",tlm_manager.reconstruction["roi_size_x"])
           self.spinBox_t3_size_y.setProperty("value",tlm_manager.reconstruction["roi_size_y"])

           # Enable Phase Unwrapping
           tlm_manager.reconstruction["phase_unwrapping_enabled"] = tlm_data.phase_unwrapping_enabled
           self.check_t4_unwrap.setProperty("checked",tlm_manager.reconstruction["phase_unwrapping_enabled"])

           # Phase Unwrapping Algorithm
           tlm_manager.reconstruction["phase_unwrapping_algorithm"] = tlm_data.phase_unwrapping_algorithm
           self.comboBox_t4_alg.setProperty("currentIndex",tlm_manager.reconstruction["phase_unwrapping_algorithm"])

           # Center Max Value
           tlm_manager.reconstruction["center_max_value"] = tlm_data.center_max_value
           self.radio_t1_max_val.setProperty("checked",tlm_manager.reconstruction["center_max_value"])

           # Wide Spectrum
           tlm_manager.reconstruction["center_wide_spectrum"] = tlm_data.center_wide_spectrum
           self.radio_t1_wide_spec.setProperty("checked",tlm_manager.reconstruction["center_wide_spectrum"])

           # Status Message
           tlm_manager.reconstruction["status_msg"] = tlm_data.status_msg

           # OTHER (Not implemented yet)
           tlm_manager.reconstruction["compute_spectral_peak"] = tlm_data.compute_spectral_peak
           tlm_manager.reconstruction["compute_digital_phase_mask"] = tlm_data.compute_digital_phase_mask
           tlm_manager.reconstruction["processing_mode"] = tlm_data.processing_mode
           tlm_manager.reconstruction["fitting_mode"] = tlm_data.fitting_mode
           tlm_manager.reconstruction["fitting_method"] = tlm_data.fitting_method
           tlm_manager.reconstruction["fitting_order"] = tlm_data.fitting_order
           tlm_manager.reconstruction["fitting_order"] = tlm_data.fitting_order
           tlm_manager.reconstruction["fitting_apply"] = tlm_data.fitting_apply
           tlm_manager.reconstruction["reset_phase_mask"] = tlm_data.reset_phase_mask
           tlm_manager.reconstruction["store_files"] = tlm_data.store_files
           tlm_manager.reconstruction["center_image"] = tlm_data.center_image
           tlm_manager.reconstruction["center_image_and_tilt"] = tlm_data.center_image_and_tilt
           tlm_manager.reconstruction["center_max_value"] = tlm_data.center_max_value
           tlm_manager.reconstruction["center_wide_spectrum"] = tlm_data.center_wide_spectrum

           
           # Set all default values
           # Need a flag that is only used ONCE when a window is first opened and should not be modified afterwards
           if(self.set_defaults == True):
               self.num_propagation_distance = tlm_manager.reconstruction["num_propagation_distance"]
               self.propagation_distance = [tlm_manager.reconstruction["propagation_distance_1"],\
                                            tlm_manager.reconstruction["propagation_distance_2"],\
                                            tlm_manager.reconstruction["propagation_distance_3"]]
               self.compute_spectral_peak = tlm_manager.reconstruction["compute_spectral_peak"]
               self.compute_digital_phase_mask = tlm_manager.reconstruction["compute_digital_phase_mask"]
               self.processing_mode = tlm_manager.reconstruction["processing_mode"]
               self.num_chromatic_shift = tlm_manager.reconstruction["num_chromatic_shift"]
               self.chromatic_shift = [tlm_manager.reconstruction["chromatic_shift_1"],\
                                       tlm_manager.reconstruction["chromatic_shift_2"]]
               self.ref_holo_path = tlm_manager.reconstruction["ref_holo_path"]
               self.ref_holo_enable = tlm_manager.reconstruction["ref_holo_enable"]
               self.ref_holo_averaging_sec = tlm_manager.reconstruction["ref_holo_averaging_sec"]
               self.ref_holo_averaging_enabled = tlm_manager.reconstruction["ref_holo_averaging_enabled"]
               self.phase_unwrapping_enabled =tlm_manager.reconstruction["phase_unwrapping_enabled"]
               self.phase_unwrapping_algorithm = tlm_manager.reconstruction["phase_unwrapping_algorithm"]
               self.fitting_mode = tlm_manager.reconstruction["fitting_mode"]
               self.fitting_method = tlm_manager.reconstruction["fitting_method"]
               self.fitting_order = tlm_manager.reconstruction["fitting_order"]
               self.fitting_apply = tlm_manager.reconstruction["fitting_apply"]
               self.reset_phase_mask = tlm_manager.reconstruction["reset_phase_mask"]
               self.roi_offset_x = tlm_manager.reconstruction["roi_offset_x"]
               self.roi_offset_y = tlm_manager.reconstruction["roi_offset_y"]
               self.roi_size_x = tlm_manager.reconstruction["roi_size_x"]
               self.roi_size_y = tlm_manager.reconstruction["roi_size_y"]
               self.store_files = tlm_manager.reconstruction["store_files"]
               self.center_image = tlm_manager.reconstruction["center_image"]
               self.center_image_and_tilt = tlm_manager.reconstruction["center_image_and_tilt"]
               self.center_max_value = tlm_manager.reconstruction["center_max_value"]
               self.center_wide_spectrum = tlm_manager.reconstruction["center_wide_spectrum"]
               self.status_msg = tlm_manager.reconstruction["status_msg"]
               
               OutputDebug("Default values are...")
               OutputDebug("Number of propagation distances: "+str(self.num_propagation_distance))
               OutputDebug("Propagation distance: "+str(self.propagation_distance))
               OutputDebug("Compute spectral peak: "+str(self.compute_spectral_peak))
               OutputDebug("Processing mode: "+str(self.processing_mode))
               OutputDebug("Number of chromatic shifts: "+str(self.num_chromatic_shift))
               OutputDebug("Chromatic shift: "+str(self.chromatic_shift))
               OutputDebug("ROI offset X: "+str(self.roi_offset_x))
               OutputDebug("ROI offset Y: "+str(self.roi_offset_y))
               OutputDebug("ROI size X: "+str(self.roi_size_x))
               OutputDebug("ROI sizy Y: "+str(self.roi_size_y))
               # Finished setting the defaults for this window session
               self.set_defaults = False
           
           self.SetTlmMode(False)
        
        # And output status messages to the DHMX debug output --
        status = tlm_data.status_msg
        status_ascii = status.decode('ASCII')
        OutputDebug("Telemetry: Reconstruction Window - "+status_ascii)


    def RevertChanges(self):
       # Send all commands as default
       OutputDebug("Resetting Reconstruction Window settings...")
       #TODO: Is there a command to read back to get the number of propagation distances?
       self.spinBox_num_dist.setProperty("value",self.num_propagation_distance)

       if(self.fitting_mode == 0):
         self.fitting_mode = "none"
       elif(self.fitting_mode == 1):
         self.fitting_mode = "1d_segment"
       elif(self.fitting_mode == 2):
         self.fitting_mode = "2d_segment"

       if(self.num_propagation_distance == 1):
          self.propagation_distances = str(self.propagation_distance[0])
       elif(self.num_propagation_distance == 2):
          self.propagation_distances = str(self.propagation_distance[0])+","+str(self.propagation_distance[1])
       elif(self.num_propagation_distance == 3):
          self.propagation_distances = str(self.propagation_distance[0])+","+str(self.propagation_distance[1])+","+str(self.propagation_distance[2])


       #Master Command for all values all at once.
       DhmCommand("reconst propagation_distance=["+self.propagation_distances+"],"+ 
              "chromatic_shift=["+str(self.chromatic_shift[0])+","+str(self.chromatic_shift[1])+"],"+  
              "fitting_mode="+str(self.fitting_mode)+","+
              "fitting_order="+str(self.fitting_order)+","+
              "roi_offset_x="+str(self.roi_offset_x)+","+
              "roi_offset_y="+str(self.roi_offset_y)+","+
              "roi_size_x="+str(self.roi_size_x)+","+
              "roi_size_y="+str(self.roi_size_y)+","+
              "center_image="+str(self.center_image)+","+
              "center_image_and_tilt="+str(self.center_image_and_tilt)+","+
              "ref_holo_enable="+str(self.ref_holo_enable)+","+
              "ref_holo_averaging_sec="+str(self.ref_holo_averaging_sec)+","+
              "phase_unwrapping_enable="+str(self.phase_unwrapping_enabled)+","+
              "ref_holo_averaging_sec="+str(self.ref_holo_averaging_sec)+","+
              "phase_unwrapping_enable="+str(self.phase_unwrapping_enabled))


       # After reset, resend telemetry and resync everything
       self.SetTlmMode(True)
       # A sleep is needed for 1 second so that dhmsw can catch up after being sent many commands at once
       time.sleep(1)
       DhmCommand("reconst")
       OutputDebug("Reverting changes complete.")






class pack_cmd_message(QObject):
   message = pyqtSignal(str,str,str,str)






class CmdWin(QObject):

  def __init__(self,):
    # CONSTRUCTOR
    super().__init__()
    self.curCmd = 0
    self.view = 0

    w.subwin_cmd.click_run.connect(self.RunCommand)

    ####self.toRecv.connect(tt.ToRecv)
   
    # Binding QML Properties to PyQt
    self.cmdEdit = w.subwin_cmd.findChild(QObject, 'text_cmd_edit')

    # This is where the command and response list objects go
    self.cmdList = w.subwin_cmd.findChild(QObject,'cmd_model')

    # the 'root' of the window
    self.cmdWindow = w.subwin_cmd.findChild(QObject,'cmd_win')

    # New message packing and list adding for QML
    self.pack_message = pack_cmd_message() # Packs the python signal into four strings
    self.pack_message.message.connect(self.cmdList.py_sig_append_cmd_list) #send the packed list back to QML


  def SetMessage(self, msg):
    self.msg = msg
    self.pack_message.message.emit(str(msg), "#000000","#00000000","2")


  def RunCommand(self):
    # Newer QML property binding
    cmd = self.cmdEdit.property("text").strip()
    if cmd == '':
      return
    else:
      recv = DhmCommand(cmd)
      self.RecvData(recv)
      

  def RecvData(self, recv):

    if len(recv) == 0:
      return
    newMsgList = recv.split(b'\x00')
    newMsg = newMsgList[0].decode()
    self.SetMessage(str(newMsg))






class MainWin(QObject):
    ## CONSTRUCTOR ##

    def __init__(self,tlm):
        super().__init__()
        # grab the global tlm object for heartbeat and other sync goodies
        self.tlm = tlm
        global open_flag
        global MAX_WAVELENGTH
        global MAX_PROPAGATION_DISTANCE
        global tlm_manager
        engine.load('qt/DhmxMain.qml')
        self.win = engine.rootObjects()[0]

        # Set version string
        self.win.version = DHMX_VERSION_STRING
        self.win.setProperty("title", DHMX_VERSION_STRING)

        # Initialize sub-window objects
        self.AboutWin = None
        self.CommandWin = None
        self.HologramWin = None
        self.FourierWin = None
        self.IntensityWin = None
        self.PhaseWin = None
        self.AmplitudeWin = None
        self.ReconWin = None
        self.ReconstWin = None
        self.ConfWin = None


        # Heartbeat timer related
        self.heartbeat_timer = QTimer()
        self.arm_heartbeat = True

        # Assign QML Objects to Python
        # # # # # # # # # # # MENU # # # # # # # # # # # #
        #MENU -> FILE
        self.menu_new_session = self.win.findChild(QObject, 'menu_new_session')
        self.menu_open_session = self.win.findChild(QObject, 'menu_open_session')
        self.menu_save_session = self.win.findChild(QObject, 'menu_save_session')
        self.menu_save_Session_as = self.win.findChild(QObject, 'menu_save_session_as')
        self.menu_close_session = self.win.findChild(QObject, 'menu_close_session')
        self.menu_exit = self.win.findChild(QObject, 'menu_exit')
        #MENU -> FRAME SOURCE
        self.menu_camera_server = self.win.findChild(QObject, 'menu_camera_server')
        self.menu_remote_location = self.win.findChild(QObject, 'menu_remote_location')
        #MENU -> FRAME SOURCE -> EXECUTE
        self.menu_run = self.win.findChild(QObject, 'menu_run')
        self.menu_idle = self.win.findChild(QObject, 'menu_idle')
        #MENU -> FRAME SOURCE -> FILE
        self.menu_hologram = self.win.findChild(QObject, 'menu_hologram')
        #MENU -> FRAME SOURCE -> FILE -> SEQUENCE
        # None
        #MENU -> FRAME SOURCE -> FILE -> SEQUENCE -> RECONSTRUCTION
        self.menu_to_disk = self.win.findChild(QObject, 'menu_to_disk')
        #MENU -> MODE
        self.menu_holograms_only = self.win.findChild(QObject, 'menu_holograms_only')
        #MENU -> RECONSTRUCTION
        self.menu_amplitude = self.win.findChild(QObject, 'menu_amplitude')
        self.menu_intensity = self.win.findChild(QObject, 'menu_intensity')
        self.menu_phase = self.win.findChild(QObject, 'menu_phase')
        self.menu_amplitude_and_phase = self.win.findChild(QObject, 'menu_amplitude_and_phase')
        self.menu_intensity_and_phase = self.win.findChild(QObject, 'menu_intensity_and_phase')
        self.menu_process_all = self.win.findChild(QObject, 'menu_process_all')
        #MENU -> SETTINGS
        self.menu_reconstruction = self.win.findChild(QObject, 'menu_reconstruction')
        self.menu_camera = self.win.findChild(QObject, 'menu_camera')
        #MENU -> SETTINGS -> PHASE UNWRAPPING
        self.menu_algorithm_1 = self.win.findChild(QObject, 'menu_algorithm_1')
        self.menu_algorithm_2 = self.win.findChild(QObject, 'menu_algorithm_2')
        self.menu_algorithm_3 = self.win.findChild(QObject, 'menu_algorithm_3')
        #MENU -> OPTIONS
        # None
        #MENU -> TOOLS
        self.menu_manual_control = self.win.findChild(QObject, 'menu_manual_control')
        #MENU -> VIEW
        self.menu_view_hologram = self.win.findChild(QObject, 'menu_view_hologram')
        self.menu_view_fourier = self.win.findChild(QObject, 'menu_view_fourier')
        self.menu_view_phase = self.win.findChild(QObject, 'menu_view_phase')
        self.menu_view_amplitude = self.win.findChild(QObject, 'menu_view_amplitude')
        self.menu_view_intensity = self.win.findChild(QObject, 'menu_view_intensity')
        #MENU -> HELP
        self.menu_about = self.win.findChild(QObject, 'menu_about')
        # # # # # # # # # # # END MENU # # # # # # # # # # # #


        # # # # # # # # # # SUB WINDOWS # # # # # # # # # # #
        # Port Window
        self.subwin_port = self.win.findChild(QObject, 'subwin_port')
        # About Window
        self.subwin_about = self.win.findChild(QObject, 'subwin_about')
        # Configuration Window
        self.subwin_conf = self.win.findChild(QObject, 'subwin_conf')
        # Reconstruction Window
        self.subwin_recon = self.win.findChild(QObject, 'subwin_recon')
        # Hologram Display
        self.subwin_holo_display = self.win.findChild(QObject, 'subwin_holo_display')
        # Phase Display
        self.subwin_phase = self.win.findChild(QObject, 'subwin_phase')
        # Amplitude Display
        self.subwin_amplitude = self.win.findChild(QObject, 'subwin_amplitude')
        # Fourier display
        self.subwin_fourier = self.win.findChild(QObject, 'subwin_fourier')
        # Intensity display
        self.subwin_intensity = self.win.findChild(QObject, 'subwin_intensity')
        # Command Window
        self.subwin_cmd = self.win.findChild(QObject, 'subwin_cmd')
        # # # # # # # # # # # # # # # # # # # # # # # # # # #

     
        # # # # # # # # # # TOOLBUTTONS # # # # # # # # # # #
        # New Session
        self.toolbutton_new_session = self.win.findChild(QObject, 'toolbutton_new_session')  
        # Open Session
        self.toolbutton_open_session = self.win.findChild(QObject, 'toolbutton_open_session')
        # Framesource
        self.framesource = self.win.findChild(QObject,'framesource')
        # Camera Framesource
        self.toolbutton_camera = self.win.findChild(QObject, 'toolbutton_camera')
        # Hologram Framesource
        self.toolbutton_framesource_hologram = self.win.findChild(QObject, 'toolbutton_framesource_hologram')
        # Sequence Framesource
        self.toolbutton_framesource_sequence = self.win.findChild(QObject, 'toolbutton_framesource_sequence')
        # Modes
        self.modes = self.win.findChild(QObject, 'modes')
        # Hologram Window
        self.toolbutton_display_hologram = self.win.findChild(QObject, 'toolbutton_display_hologram')
        # Amplitude Window
        self.toolbutton_display_amplitude = self.win.findChild(QObject, 'toolbutton_display_amplitude')
        # Intensity Window
        self.toolbutton_display_intensity = self.win.findChild(QObject, 'toolbutton_display_intensity')
        # Phase Window
        self.toolbutton_display_phase = self.win.findChild(QObject, 'toolbutton_display_phase') 
        # Fourier Window
        self.toolbutton_display_fourier = self.win.findChild(QObject, 'toolbutton_display_fourier')
        # Run and Idle
        self.run_and_idle = self.win.findChild(QObject, 'run_and_idle')
        # Run
        self.toolbutton_run = self.win.findChild(QObject, 'toolbutton_run') 
        # Idle
        self.toobutton_idle = self.win.findChild(QObject, 'toolbutton_idle')
        # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # # # # # # # # # # # OTHER # # # # # # # # # # # # #
        self.dhmx_fd_cmd = self.win.findChild(QObject, 'dhmx_fd_cmd')
        self.dhmx_fd_generic = self.win.findChild(QObject, 'dhmx_fd_generic')
        self.text_status  = self.win.findChild(QObject, 'text_status')
        self.icon_heartbeat_status = self.win.findChild(QObject, 'icon_heartbeat_status')
        self.icon_datalogger_status = self.win.findChild(QObject, 'icon_datalogger_status')
        self.icon_controller_status = self.win.findChild(QObject, 'icon_controller_status')
        self.icon_guiserver_status = self.win.findChild(QObject, 'icon_guiserver_status')
        self.icon_reconstructor_status = self.win.findChild(QObject, 'icon_reconstructor_status')
        self.icon_framesource_status = self.win.findChild(QObject, 'icon_framesource_status')
        # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Connect QML signals to Python slots
        self.win.qml_signal_close.connect(self.Shutdown)
        self.tlm.DhmxTlm.tlm_data_heartbeat.connect(self.UpdateTlm)

        # NOTE: If the signal is coming from a menu item that is meant to send
        # a command, it will not call a function.  Instead it will just send
        # a command inline with the signal/slot assignment using a lambda
        self.menu_exit.qml_signal_quit.connect(self.Shutdown)
        self.menu_camera_server.qml_signal_camera_server.connect(lambda: self.SendGenericCommand('framesource mode='+SetFrameSourceMode('camera'), self.framesource,1))
        self.menu_run.qml_signal_run.connect(lambda: self.SendGenericCommand('framesource exec=run',self.run_and_idle,1))
        self.menu_idle.qml_signal_idle.connect(lambda: self.SendGenericCommand('framesource exec=idle',self.run_and_idle,2))
        self.menu_holograms_only.qml_signal_holograms_only.connect(lambda: self.SendGenericCommand('reconst processing_mode=off',self.modes,1))
        self.menu_amplitude.qml_signal_reconst_amplitude.connect(lambda: self.SendGenericCommand('reconst processing_mode=amp',self.modes, 2))
        self.menu_intensity.qml_signal_reconst_intensity.connect(lambda: self.SendGenericCommand('reconst processing_mode=intensity',self.modes, 3))
        self.menu_phase.qml_signal_reconst_phase.connect(lambda: self.SendGenericCommand('reconst processing_mode=phase', self.modes, 4))
        self.menu_amplitude_and_phase.qml_signal_reconst_amplitude_and_phase.connect(lambda: self.SendGenericCommand('reconst processing_mode=amp_and_phase',self.modes,5))
        self.menu_intensity_and_phase.qml_signal_reconst_intensity_and_phase.connect(lambda: self.SendGenericCommand('reconst processing_mode=int_and_phase',self.modes,6))
        self.menu_process_all.qml_signal_process_all.connect(lambda: self.SendGenericCommand('reconst processing_mode=all',self.modes,7))

        # special commands that require a file dialog
        self.menu_hologram.qml_signal_hologram_open_fd.connect(self.OpenHologram)
        self.menu_to_disk.qml_signal_to_disk_open_fd.connect(self.OpenToDisk)
        self.toolbutton_open_session.qml_signal_open_session.connect(self.LoadSessionCfgFile)


        # The file dialog signal / slot to return a filepath along with the command that opened it 
        self.dhmx_fd_cmd.qml_signal_send_file_path.connect(self.HandleFdCmd)

        # Connect subwindow signals to classes to manage their functionalities
        self.menu_about.qml_signal_launch_about.connect(self.LaunchAboutWindow)
        self.menu_manual_control.qml_signal_launch_command_window.connect(self.LaunchCommandWindow)
        self.menu_view_hologram.qml_signal_launch_holo_display.connect(self.LaunchHologramWindow)
        self.menu_view_fourier.qml_signal_launch_fourier_display.connect(self.LaunchFourierWindow)
        self.menu_view_phase.qml_signal_launch_phase_display.connect(self.LaunchPhaseWindow)
        self.menu_view_amplitude.qml_signal_launch_amplitude_display.connect(self.LaunchAmplitudeWindow)
        self.menu_view_intensity.qml_signal_launch_intensity_display.connect(self.LaunchIntensityWindow)
        self.menu_reconstruction.qml_signal_launch_reconstruction_window.connect(self.LaunchReconstructionWin)
        self.menu_new_session.qml_signal_launch_configuration_window.connect(self.LaunchConfigurationWin)

        # Special qml signals
        # Launching seperate programs
        self.menu_camera.qml_signal_launch_dhmxc.connect(self.LaunchDhmxc)


        # Get initial telemetry for wavelengths and propagations distances, this is used
        # Throughout DHMx
        DhmCommand('reconst') # For propagation distance
        time.sleep(0.100) # Just a momentary pause so that that TCP handshake occurs orderly.
        DhmCommand('session') # For wavelengths
        



    def Shutdown(self):
       DhmCommand("shutdown")
       QApplication.quit()



    def SendGenericCommand(self,cmd,callback=None,combo=None):
       ret = DhmCommand(cmd)
       print(ret.decode('ascii'))
       try:
          if(callback != None and combo == None):
             if 'ACK' in ret.decode('ascii'):
                callback.setSelected()
          elif(callback != None and combo != None):
             if 'ACK' in ret.decode('ascii'):
                callback.setSelected(combo)
       except:
          print("No Callback.")


    def LoadSessionCfgFile(self):
       cfg = LoadFile("ses",int(w.subwin_conf.property("x"))+int((w.subwin_conf.property("width")/2)), \
               int(w.subwin_conf.property("y"))+ int((w.subwin_conf.property("height")/2)),\
               "/home","Load Session File")
       DhmCommand(cfg)
       DhmCommand("session")


    def HandleFdCmd(self, path, cmd,callback_func=None,callback_selection=None):
       # Send DHM command
       ret = DhmCommand(cmd%path)

       # return to another function
       if(callback_func != None and callback_selection != None):
          if 'ACK' in ret.decode('ascii'):
             callback_func.setSelected(callback_selection)


    def OpenHologram(self):
       self.win.open_file_dialog('Select a file','framesource mode='+SetFrameSourceMode('file')+',filepath=%s',False,False,self.framesource,2)


    #TOOD: rmeove todisk and todisplay and call it sequence
    def OpenToDisk(self):
       self.win.open_file_dialog('Select a folder','framesource mode='+SetFrameSourceMode('sequence')+',filepath=%s',False,True,self.framesource,3)#reconst store_files=yes seperate command


    def OpenToDisplay(self):
       self.win.open_file_dialog('Select a folder','framesource mode='+SetFrameSourceMode('sequence')+',filepath=%s',False,True)


    def LaunchCommandWindow(self):
      if(self.CommandWin == None):
         self.CommandWin = CmdWin() 


#    def LaunchPortWindow(self):

#       def ApplyPorts():
#         global RAW_FRAME_PORT,           \
#                RECONST_AMP_FRAME_PORT,   \
#                RECONST_INT_FRAME_PORT,   \
#                RECONST_PHASE_FRAME_PORT, \
#                FOURIER_FRAME_PORT,       \
#                COMMAND_SERVER_PORT,      \
#                FRAME_SERVER_PORT,        \
#                TELEMETRY_SERVER_PORT,    \
#                PORT
#         RAW_FRAME_PORT = int(port_raw_frame.property("text"))
#         RECONST_AMP_FRAME_PORT = int(port_amplitude.property("text"))
#         RECONST_INT_FRAME_PORT = int(port_intensity.property("text"))
#         RECONST_PHASE_FRAME_PORT = int(port_phase.property("text"))
#         FOURIER_FRAME_PORT = int(port_fourier.property("text"))
#         self.tlm.port = int(port_telemetry.property("text"))
         
         # The command port used by DHMSW / DHMx to send commands
#         PORT = int(port_command.property("text"))
 
         ######
         #Frame server disabled for now
#         COMMAND_SERVER_PORT = int(port_command_server.property("text"))
#         FRAME_SERVER_PORT = int(port_frame_server.property("text"))
#         TELEMETRY_SERVER_PORT = int(port_telemetry_server.property("text"))

         #Telemetry server port disabled for now
#         self.subwin_port.setProperty("visible",False)


#       self.subwin_port.setProperty("visible", True)
#       x_port = (int(self.win.property("width"))/2) - (int(self.subwin_port.property("width"))/2)
#       y_port = (int(self.win.property("height"))/2) - (int(self.subwin_port.property("height"))/2)
#       self.subwin_port.setProperty("x", x_port-100)
#       self.subwin_port.setProperty("y", y_port-150)
#       port_fourier = self.subwin_port.findChild(QObject, "textInput_fourier")
#       port_amplitude = self.subwin_port.findChild(QObject, "textInput_amplitude")
#       port_raw_frame = self.subwin_port.findChild(QObject, "textInput_raw_frame")
#       port_intensity = self.subwin_port.findChild(QObject, "textInput_intensity")
#       port_phase =  self.subwin_port.findChild(QObject, "textInput_phase")
#       port_telemetry = self.subwin_port.findChild(QObject, "textInput_telemetry")
#       port_command = self.subwin_port.findChild(QObject, "textInput_command")
       #########
#       port_frame_server = self.subwin_port.findChild(QObject, "textInput_frame_server")
#       port_command_server = self.subwin_port.findChild(QObject, "textInput_command_server")
#       port_telemetry_server = self.subwin_port.findChild(QObject, "textInput_telemetry_server")
#       button_apply = self.subwin_port.findChild(QObject, "button_apply")
#       button_cancel = self.subwin_port.findChild(QObject, "button_cancel")

       # Temporarily disable Frame Server Port and Telemetry Server Port (Will enable in future versions)
#       port_frame_server.setProperty("enabled",False)
#       port_telemetry_server.setProperty("enabled",False)

#       button_apply.clicked.connect(ApplyPorts)



    def LaunchAboutWindow(self):
       x_about = (int(self.win.property("width"))/2) - (int(self.subwin_about.property("width"))/2)
       y_about = (int(self.win.property("height"))/2) - (int(self.subwin_about.property("height"))/2)
       self.subwin_about.setProperty("version",DHMX_VERSION_STRING)
       self.subwin_about.setProperty("x", x_about)
       self.subwin_about.setProperty("y", y_about)


    # For holograms only
    def LaunchHologramWindow(self):
       DhmCommand("guiserver enable_rawframes=true")
       if(self.HologramWin == None):
          self.HologramWin = HologramWin(self.tlm)
       else:
          self.HologramWin.OpenWin()
       self.toolbutton_display_hologram.setSelected()
       self.HologramWin.BeginPlayback()
       SetFrameSourceMode(GetFrameSourceMode())


    def LaunchAmplitudeWindow(self):
       DhmCommand("guiserver enable_amplitude=true")
       if(self.AmplitudeWin == None):
          self.AmplitudeWin = AmplitudeWin(self.tlm)
       else:
          self.AmplitudeWin.OpenWin()
       self.toolbutton_display_amplitude.setSelected()
       self.AmplitudeWin.BeginPlayback()
       SetFrameSourceMode(GetFrameSourceMode())


    def LaunchPhaseWindow(self):
       DhmCommand("guiserver enable_phase=true")
       if(self.PhaseWin == None):
          self.PhaseWin = PhaseWin(self.tlm)
       else:
          self.PhaseWin.OpenWin()
       self.toolbutton_display_phase.setSelected()
       self.PhaseWin.BeginPlayback()
       SetFrameSourceMode(GetFrameSourceMode())


    def LaunchIntensityWindow(self):
       DhmCommand("guiserver enable_intensity=true")
       if(self.IntensityWin == None):
          self.IntensityWin = IntensityWin(self.tlm)
       else:
          self.IntensityWin.OpenWin()
       self.toolbutton_display_intensity.setSelected()
       self.IntensityWin.BeginPlayback()
       SetFrameSourceMode(GetFrameSourceMode())


    def LaunchFourierWindow(self):
       DhmCommand("guiserver enable_fourier=true")
       if(self.FourierWin == None):
          self.FourierWin = FourierWin(self.tlm)
       else:
          self.FourierWin.OpenWin()
       self.toolbutton_display_fourier.setSelected()
       self.FourierWin.BeginPlayback()
       SetFrameSourceMode(GetFrameSourceMode())


    def LaunchReconstructionWin(self):
       if(self.ReconWin == None):
          self.ReconWin = ReconstructionWin(self.tlm)
       else:
          self.ReconWin.Show()


    def LaunchConfigurationWin(self):
       if(self.ConfWin == None):
          self.ConfWin = ConfigurationWin(self.tlm)
       DhmCommand("session")
       self.ConfWin.SetTlmMode(True)
       self.toolbutton_new_session.setSelected()


    def LaunchDhmxc(self):
       global COMMAND_SERVER_PORT
       subprocess.Popen([sys.executable,"dhmxc.py","--cmdserver", str(COMMAND_SERVER_PORT),"--frameserver",str(FRAME_SERVER_PORT), "--tlmserver",str(TELEMETRY_SERVER_PORT) ])



    def UpdateTlm(self,tlm_data):
      tlm_manager.heartbeat["status_message"] = (tlm_data.status_msg.split(b'\0',1)[0].decode('ASCII'))
      # Heartbeat
      # If for any reason the heartbeat stops, all other services go red
      #self.icon_heartbeat_status
      if(self.arm_heartbeat == True):
         # arm the heartbeat by setting expiration of 2 seconds
         self.icon_heartbeat_status.armTimer(2000)
         # Heartbeat armed.
         self.arm_heartbeat = False
      # Telemetry is received within 3 seconds, reset the timer.
      else:
         self.icon_heartbeat_status.resetTimer()
         
      # Datalogger
      tlm_manager.heartbeat["datalogger_status"] = tlm_data.status[0]
      self.icon_datalogger_status.setMode(tlm_manager.heartbeat["datalogger_status"])

      # Controller
      tlm_manager.heartbeat["controller_status"] = tlm_data.status[1]
      self.icon_controller_status.setMode(tlm_manager.heartbeat["controller_status"])

      # GUI Server
      tlm_manager.heartbeat["guiserver_status"] = tlm_data.status[2]
      self.icon_guiserver_status.setMode(tlm_manager.heartbeat["guiserver_status"])

      # Reconstructor
      tlm_manager.heartbeat["reconstructor_status"] = tlm_data.status[3]
      self.icon_reconstructor_status.setMode(tlm_manager.heartbeat["reconstructor_status"])

      # Framesource
      tlm_manager.heartbeat["framesource_status"] = tlm_data.status[4]
      self.icon_framesource_status.setMode(tlm_manager.heartbeat["framesource_status"])

      # Status Message
      if(tlm_manager.heartbeat["status_message"] != ""):
        self.text_status.setProperty("text", tlm_manager.heartbeat["status_message"])
########################################################################################################







### MAIN ####
## This will launch the Qt QML engine and launch the main QML window
if __name__ == "__main__":
    #Parse in arguments on launch
    parser = OptionParser()

    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                    help="Turn on verbose mode for debugging.")
    parser.add_option("-V", "--version", action="store_true", dest="version",
                    help="Read version of DHMx.")
    parser.add_option("-l","--log",dest="logging",
                    help="Generate a log file for DHMx wich will be stored in its log dir.")
    # DHM Specific Port
    parser.add_option("--dhmcommand", dest="dhmCommandServerPort",
                    help="Override the default DHM Command Server port.")
    parser.add_option("--tlm", dest="dhmTelemetryServerPort",
                    help="Override the default port for the Gui Server's raw display.")

    # GUI Server specific ports
    parser.add_option("--phase", dest="phasePort",
                    help="Override the default port for the Gui Server's phase display.")
    parser.add_option("--intensity", dest="intensityPort",
                    help="Override the default port for the Gui Server's intensity display.")
    parser.add_option("--raw", dest="rawPort",
                    help="Override the default port for the Gui Server's raw display.")
    parser.add_option("--amplitude", dest="amplitudePort",
                    help="Override the default port for the Gui Server's phase display.")
    parser.add_option("--fourier", dest="fourierPort",
                    help="Override the default port for the Gui Server's intensity display.")

    # Camera Server specific Ports
    parser.add_option("--frameserver", dest="frameServerPort",
                    help="Override the Camera Server's default Frame Server port.")
    parser.add_option("--cmdserver", dest="commandServerPort",
                    help="Override the Camera Server's default Command Server's port.")
    parser.add_option("--tlmserver", dest="telemetryServerPort",
                    help="Override the Camera Server's default Telemetry Server port.")


    # parse in the arguments
    (opts, args) = parser.parse_args()


    # if the user asks for -v/--version, print the version and exit
    if(opts.version):
       print(DHMX_VERSION_STRING)
       exit(0)
       
    # Log to a file if a user enables the command
    if(opts.logging):
       # Clean up the file path in case someone has or does not have a '/' at the end of their path
       dir_path = opts.logging.rstrip('/')
       
       # Create the log filename.  It will be based on UTC time
       log_filename = ('DHMx_log_'+str(datetime.utcnow())+'.log')

       # Create and start logging.  
       logging.basicConfig(filename=dir_path+"/"+log_filename,level=logging.DEBUG)


    # Prepare the QML engine
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()


    # Update global variables with this class. Any changes to wavelength or
    # Prop distance is connected via pyqt signal
    OutputDebug("Asking dhmsw for wavelength and propagation distance used for display windows...")
    wl_and_prop = UpdateWavelengthAndProp()

    #FML: EXPERIMENTAL
    OutputDebug("Creating service providers for display windows...")
    provider_hologram = HologramImageProvider()
    provider_phase = PhaseImageProvider()
    provider_amplitude = AmplitudeImageProvider()
    provider_fourier = FourierImageProvider()
    provider_intensity = IntensityImageProvider()
    engine.addImageProvider("Hologram", provider_hologram)
    engine.addImageProvider("Phase", provider_phase)
    engine.addImageProvider("Amplitude", provider_amplitude)
    engine.addImageProvider("Fourier", provider_fourier)
    engine.addImageProvider("Intensity", provider_intensity)

    # Video conversion testing - please remove
    #vc.img_to_mp4(image_format="/home/qt/git/DHMX_0.7.x/test_sets/set01/Holograms/%05d_holo.tif")

    # Set custom ports if specified
    if(opts.dhmCommandServerPort): SetDhmCommandServerPort(opts.dhmCommandServerPort)
    if(opts.dhmTelemetryServerPort): SetDhmTelemetryServerPort(opts.dhmTelemetryServerPort)
    if(opts.phasePort):  SetPhasePort(opts.phasePort)
    if(opts.intensityPort): SetIntensityPort(opts.intensityPort)
    if(opts.rawPort): SetRawPort(opts.rawPort)
    if(opts.amplitudePort): SetAmplitudePort(opts.amplitudePort)
    if(opts.fourierPort): SetFourierPort(opts.fourierPort)
    if(opts.frameServerPort): SetFrameServerPort(opts.frameServerPort)
    if(opts.commandServerPort): SetCommandServerPort(opts.commandServerPort)
    if(opts.telemetryServerPort): SetTelemetryServerPort(opts.telemetryServerPort)

    # Startup telemetry services
    OutputDebug("Starting up telemetry...")
    tlm = DhmxTelemetry()
    tlm_manager = TelemetryManager(tlm)


    # Load up the main window
    OutputDebug("Creating the main window...")
    # Launch main window
    w = MainWin(tlm)

    # Begin Qt Execution
    OutputDebug("Executing Qt engine.")
    app.exec_()

    # Cleanup main thread
    sys.exit()
################################################################################
