###############################################################################
#  Copyright 2019, by the California Institute of Technology. ALL RIGHTS RESERVED. 
#  United States Government Sponsorship acknowledged. Any commercial use must be 
#  negotiated with the Office of Technology Transfer at the 
#  California Institute of Technology.
#
#  This software may be subject to U.S. export control laws. By accepting this software, 
#  the user agrees to comply with all applicable U.S. export laws and regulations. 
#  User has the responsibility to obtain export licenses, or other export authority 
#  as may be required before exporting such information to foreign countries or providing 
#  access to foreign persons.
#
#  file:	controller.py
#  author:	S. Felipe Fregoso
#  brief:	Controls telemetry and signal reconstruction done
#               
#              
###############################################################################
import socket
import numpy as np
import select
import multiprocessing
import time
import queue
import copy

from . import interface
from . import telemetry_iface_ag
from . import metadata_classes
from .dhm_cmd_client_server import (DHM_Command_Server)
from .framesource import Framesource
from .reconstructor import Reconstructor
from .guiserver import Guiserver
from .dhmcommands import CommandDictionary
from .heartbeat import Heartbeat

class Controller(multiprocessing.Process):
    def __init__(self, _qs, pub, _events, configfile=None, verbose=False):

        multiprocessing.Process.__init__(self)

        self._verbose = verbose
        self._module_init_count = 0
        self._qs = _qs
        self._events = _events
        self._pub = pub
        ### Heartbeat
        self._HB = None

        self._cmdDict = CommandDictionary()

        ### Command server handler
        self._cmd_server = None 

        ### Telemetry Objects
        self._reconst_telem = None
        self._session_telem = None
        self._heartbeat_telem = None
        self._holo_telem = None
        self._framesource_telem = None
        self._datalogger_telem = None
        self._guiserver_telem = None
        self._fouriermask_telem = None

        ### 
        meta = metadata_classes.Metadata_Dictionary(configfile)
        self._meta             = meta.metadata['CONTROLLER']
        self._reconst_meta     = meta.metadata['RECONSTRUCTION']
        self._holo_meta        = meta.metadata['HOLOGRAM']
        self._framesource_meta = meta.metadata['FRAMESOURCE']
        self._datalogger_meta  = meta.metadata['DATALOGGER']
        self._guiserver_meta   = meta.metadata['GUISERVER']
        self._session_meta     = meta.metadata['SESSION']
        self._fouriermask_meta = meta.metadata['FOURIERMASK']
        pass

    def holometa_to_telem(self, meta):
        self._holo_telem.set_values(len(meta.wavelength),meta.wavelength,meta.dx,meta.dy,meta.crop_fraction,meta.rebin_factor,meta.bgd_sub,meta.bgd_file)
        return self._holo_telem.pack()
    def framesourcemeta_to_telem(self, meta):
        self._framesource_telem.set_values(meta.state,
                                           meta.mode,
                                           meta.file['datadir'],
                                           meta.file['currentfile'],
                                           meta.status_msg)
        return self._framesource_telem.pack()
    def dataloggermeta_to_telem(self, meta):
        self._datalogger_telem.set_values(meta.enabled,
                                          "",
                                          meta.status_msg)
        return self._datalogger_telem.pack()
    def guiservermeta_to_telem(self, meta):
        self._guiserver_telem.set_values([meta.ports['fourier'],meta.ports['reconst_amp'],meta.ports['raw_frames'],meta.ports['telemetry']],
                                         meta.connection_status[0:4],
                                         meta.status_msg)
        return self._guiserver_telem.pack()

    def sessionmeta_to_telem(self, meta):
#        print( meta.name,
#                                        meta.description,
#                                        len(meta.holo.wavelength),
#                                        meta.holo.wavelength,
#                                        meta.holo.dx,
#                                        meta.holo.dy,
#                                        meta.holo.crop_fraction,
#                                        meta.holo.rebin_factor,
#                                        meta.lens.focal_length,
#                                        meta.lens.numerical_aperture,
#                                        meta.lens.system_magnification,
#                                        '')
        self._session_telem.set_values( meta.name,
                                        meta.description,
                                        len(meta.holo.wavelength),
                                        meta.holo.wavelength,
                                        meta.holo.dx,
                                        meta.holo.dy,
                                        int(meta.holo.crop_fraction),
                                        int(meta.holo.rebin_factor),
                                        meta.lens.focal_length,
                                        meta.lens.numerical_aperture,
                                        meta.lens.system_magnification,
                                        meta.status_msg)
        return self._session_telem.pack()

    def fouriermaskmeta_to_telem(self, meta):
        x_peak = [circ.get_params[0] for circ in meta.mask.circle_list]
        num_x_peak = len(x_peak)
        y_peak = [circ.get_params[1] for circ in meta.mask.circle_list]
        num_y_peak = len(y_peak)
        mask = np.any(meta.mask.mask, axis=2).flatten()
        self._fouriermask_telem.set_values(
                        num_x_peak,
                        x_peak,
                        num_y_peak,
                        y_peak,
                        mask,
                        )
        return self._fouriermask_telem.pack()

    def reconstmeta_to_telem(self, meta):

        self._reconst_telem.set_values(
                        len(meta.propagation_distance), 
                        meta.propagation_distance, 
                        meta.compute_spectral_peak, 
                        meta.compute_digital_phase_mask, 
                        meta.processing_mode, 
                        len(meta.chromatic_shift), 
                        meta.chromatic_shift, 
                        meta.ref_holo.path, 
                        meta.ref_holo.enabled, 
                        meta.ref_holo.averaging_sec, 
                        meta.ref_holo.averaging_enabled, 
                        meta.phase_unwrapping.enabled, 
                        meta.phase_unwrapping.algorithm,
                        meta.fitting.mode, 
                        meta.fitting.method, 
                        meta.fitting.order, 
                        meta.fitting.applied, 
                        meta.phase_mask_reset, 
                        meta.roi_x.offset, 
                        meta.roi_y.offset, 
                        meta.roi_x.size, 
                        meta.roi_y.size, 
                        meta.store_files, 
                        meta.center_image.center, 
                        meta.center_image.center_and_tilt, 
                        meta.center_image.max_value, 
                        meta.center_image.wide_spectrum, 
                        meta.status_msg)
        return self._reconst_telem.pack()

    def send_telemetry(self, telem_bin_str, srcid):
        a = interface.MessagePkt(interface.TELEMETRY_TYPE, srcid)
        a.append(telem_bin_str)
        a.complete_packet()
        b = interface.GuiPacket('telemetry', a.to_bytes())
        self._qs['guiserver_inq'].put_nowait(b)
        #print("Controller sending telemetry: ", time.time())

    def publish_session_status(self, status_msg=None):
        if status_msg:
            self._session_meta.status_msg = status_msg
        #self._qs['controller_inq'].put_nowait(interface.MetadataPacket(self._session_meta))
        self._pub.publish('session_status', interface.MetadataPacket(self._session_meta))

    def command_dispatcher(self, data):
        cmd = data.get_cmd()
        #print('Controller received command')
        #print(cmd)
        #print(time.time())
        for k, v in cmd.items():
            if k == 'reconst' or k == 'holo' or k == 'fouriermask':
                self._qs['reconstructor_inq'].put_nowait(data)
            elif k == 'framesource':
                self._qs['framesource_inq'].put_nowait(data)
            elif k == 'guiserver':
                self._qs['guiserver_inq'].put_nowait(data)
            elif k == 'datalogger':
                self._qs['datalogger_inq'].put_nowait(data)
            elif k == 'session':
                tempsession = copy.copy(self._session_meta)
                tempsession.holo =  copy.copy(self._holo_meta)
                validcmd = True
                if not v: ### Empty parameter list, send reconst status
                    #self._qs['controller_inq'].put_nowait(interface.MetadataPacket(tempsession))
                    self.publish_session_status(status_msg="SUCCESS")
                    break
                for param, value in v.items():
                    if param == 'name':
                        tempsession.name = value;
                    elif param == 'description':
                        tempsession.description = value;
                    elif param == 'wavelength':
                        tempsession.holo.wavelength = value;
                    elif param == 'dx':
                        tempsession.holo.dx = value;
                    elif param == 'dy':
                        tempsession.holo.dy = value;
                    elif param == 'crop_fraction':
                        tempsession.holo.crop_fraction = value;
                    elif param == 'rebin_factor':
                        tempsession.holo.rebin_factor = value;
                    elif param == 'focal_length':
                        tempsession.lens.focal_length = value;
                    elif param == 'numerical_aperture':
                        tempsession.lens.numerical_aperture = value;
                    elif param == 'system_magnification':
                        tempsession.lens.system_magnification = value;
                    else:
                        validcmd = False
                        pass
                if validcmd:
                    self._session_meta = copy.copy(tempsession)
                    self._holo_meta = copy.copy(tempsession.holo)
                    # Send holo data to 
                    self._qs['reconstructor_inq'].put_nowait(self._holo_meta)
                    #self._qs['controller_inq'].put_nowait(interface.MetadataPacket(self._session_meta))
                    self.publish_session_status(status_msg="SUCCESS")
    
    #                    elif k == 'camera':
    #                        tempcamera = copy.copy(camera_meta)
    #                        for param, value in v.items():
    #                            if param == 'gain':
    #                                tempcamera.gain = param;
    #                            elif param == 'brightness':
    #                                tempcamera.brightness= param;
    #                            elif param == 'shutter':
    #                                tempcamera.shutter = param;
    #                            elif param == 'framerate':
    #                                tempcamera.framrate = param;
    #                            elif param == 'row':
    #                                tempcamera.row = param;
    #                            elif param == 'col':
    #                                tempcamera.col = param;
    #                            elif param == 'width':
    #                                tempcamera.width = param;
    #                            elif param == 'height':
    #                                tempcamera.height = param;
            elif k == 'shutdown':
                for kk, vv in self._qs.items():
                    vv.put_nowait(None)
            else:
                pass
        pass

    def process_meta(self, data):
        if type(data) is interface.MetadataPacket:
            meta = data.meta
        else:
            meta = data

        metatype = type(meta)

        if metatype is metadata_classes.Reconstruction_Metadata:
            self._reconst_meta = data.meta
            self.send_telemetry(self.reconstmeta_to_telem(data.meta), interface.SRCID_TELEMETRY_RECONSTRUCTION)
        elif metatype is metadata_classes.Fouriermask_Metadata:
            #print('Received Fouriermask_Metadata')
            self._fouriermask_meta = data.meta
            self.send_telemetry(self.fouriermaskmeta_to_telem(data.meta), interface.SRCID_TELEMETRY_FOURIERMASK)
        elif metatype is metadata_classes.Session_Metadata:
            #print('Received Session_Metadata')
            self._session_meta = data.meta
            self.send_telemetry(self.sessionmeta_to_telem(data.meta), interface.SRCID_TELEMETRY_SESSION)
        elif metatype is metadata_classes.Hologram_Metadata:
            #print('Received Hologram_Metadata')
            self._holo_meta = data.meta
            self.send_telemetry(self.holometa_to_telem(data.meta), interface.SRCID_TELEMETRY_HOLOGRAM)
            pass
        elif metatype is metadata_classes.Framesource_Metadata:
            #print('Received Framesource_Metadata')
            self._framesource_meta = data.meta
            self.send_telemetry(self.framesourcemeta_to_telem(data.meta), interface.SRCID_TELEMETRY_FRAMESOURCE)
        elif metatype is metadata_classes.Datalogger_Metadata:
            #print('Received Datalogger_Metadata')
            self._datalogger_meta = data.meta
            self.send_telemetry(self.dataloggermeta_to_telem(data.meta), interface.SRCID_TELEMETRY_DATALOGGER)
        elif metatype is metadata_classes.Guiserver_Metadata:
            #print('Received Guiserver_Metadata')
            self._guiserver_meta = data.meta
            self.send_telemetry(self.guiservermeta_to_telem(data.meta), interface.SRCID_TELEMETRY_GUISERVER)
        elif metatype is metadata_classes.Reconstruction_Done_Metadata:
            self._events['reconst']['done'].set()
        else:
            print('Unknown metadata type')
    
    def initialize(self):
        self._reconst_telem = telemetry_iface_ag.Reconstruction_Telemetry() 
        self._session_telem = telemetry_iface_ag.Session_Telemetry()
        self._heartbeat_telem = telemetry_iface_ag.Heartbeat_Telemetry()
        self._holo_telem = telemetry_iface_ag.Hologram_Telemetry()
        self._framesource_telem = telemetry_iface_ag.Framesource_Telemetry()
        self._datalogger_telem = telemetry_iface_ag.Datalogger_Telemetry()
        self._guiserver_telem = telemetry_iface_ag.Guiserver_Telemetry()
        self._fouriermask_telem = telemetry_iface_ag.Fouriermask_Telemetry()

        ### Create heartbeat thread
        ### Start the Heartbeat thread
        self._HB = Heartbeat(self._pub, 'controller')
        self._HB.start()
    
    def process_initdone(self, data):
        #print('Controller: Received "initdone" from [%s], errcode=%d'%(data._name, data._errorcode))
        if data._errorcode == 0:
            self._module_init_count += 1

        if self._module_init_count >= 5:
            self._events['controller']['start'].set()
            if self._cmd_server is None:
                self._cmd_server = DHM_Command_Server(q=self._qs['controller_inq'], validate_func=self._cmdDict.validate_command, hostname=self._meta.cmd_hostname, port=self._meta.cmd_port)
            self._cmd_server.start()
            print('Controller: Starting command server...')

    def run(self):
        try:
            self.initialize()

            print('Controller Consumer thread started')

            processing_reconst = False
            while True:
                data = self._qs['controller_inq'].get()
                if data is None:
                    print('Exiting Controller')
                    break
    
                ### Process command
                datatype = type(data)
    
                if datatype is interface.InitDonePkt:
                    self.process_initdone(data)

                ### Process Metadata Packets by converting them to telemetry
                elif isinstance(data, interface.MetadataPacket):
                    self.process_meta(data)
    
                elif datatype is interface.Command:
                    print('%f: Got command!'%(time.time()))
                    ### Dispatch the command to the responsible module
                    self.command_dispatcher(data)
                                
                ### Process image (from camera streamer)
                elif datatype is interface.Image:
                    pass
    
                elif datatype is interface.ReconstructorProduct:
    
                    print("%f: Got reconstructor data!"%(time.time()))
                    processing_reconst = False

                    #if data.reconst_meta.processing_mode == metadata_classes.Reconstruction_Metadata.RECONST_NONE:
                    #    continue
                    #else:
                    #    reconst_done_event.set()
    
                else:
                    print('Controller:  Unknown data type')
            ## End of While
            self._HB.terminate()
                
        except Exception as e:
            print('Controller Exception caught: %s'%(repr(e)))
            # Store exception and notify the heartbeat thread
            self._HB.set_update(e)

            # Wait for heartbeat thread to return
            if self._HB.isAlive():
                print('Heartbeat is ALIVE')
                self._HB.join(timeout=5)

            ## Die!
            raise e
        finally:
            pass
   
if __name__ == '__main__':
    print('Main executed')
    import multiprocessing as mp
    import numpy as np
    import dhmpubsub as pubsub
    from dhmcommands import CommandDictionary
    img = interface.Image((1,2,3), np.zeros((2048,2048), dtype=np.float32))

  ### Create Message Queues
    ctx = mp.get_context('spawn')
    _qs = {}
    _qs['controller_inq']    = ctx.Queue()
    _qs['framesource_inq']   = ctx.Queue()
    _qs['reconstructor_inq'] = ctx.Queue()
    _qs['guiserver_inq']     = ctx.Queue()
    _qs['datalogger_inq']    = ctx.Queue()
    _qs['watchdog_inq']      = ctx.Queue()

    ### Make the publish/subscribe connections
    pub = pubsub.PubSub()
 
    #published by all modules to indicate that it is done initializing
    pub.subscribe('init_done', _qs['controller_inq'])

    # Subscribe to RAW FRAMES
    #pub.subscribe('rawframe', _qs['guiserver_inq'])
    pub.subscribe('rawframe', _qs['reconstructor_inq'])
    # Subscribe to RECONSTRUCTION PRODUCTS
    pub.subscribe('reconst_product', _qs['guiserver_inq'])

    pub.subscribe('reconst_done', _qs['framesource_inq'])
    pub.subscribe('reconst_done', _qs['controller_inq'])

    #-- Subscribe to STATUS messages
    #  Reconst Status
    pub.subscribe('reconst_status', _qs['controller_inq'])
    pub.subscribe('reconst_status', _qs['framesource_inq'])
    pub.subscribe('reconst_status', _qs['guiserver_inq'])
    #    Holo Status
    pub.subscribe('holo_status', _qs['controller_inq'])
    pub.subscribe('fouriermask_status', _qs['controller_inq'])
    pub.subscribe('session_status', _qs['controller_inq'])
    pub.subscribe('framesource_status', _qs['controller_inq'])
    pub.subscribe('datalogger_status', _qs['controller_inq'])
    pub.subscribe('guiserver_status', _qs['controller_inq'])
    pub.subscribe('watchdog_status', _qs['guiserver_inq'])
    # Subscribe to TELEMETRY messages
    #pub.subscribe('reconst_telemetry', _qs['guiserver_inq'])
    #pub.subscribe('holo_telemetry', _qs['guiserver_inq'])
    #pub.subscribe('fouriermask_telemetry', _qs['guiserver_inq'])
    #pub.subscribe('session_telemetry', _qs['guiserver_inq'])
    #pub.subscribe('framesource_telemetry', _qs['guiserver_inq'])
    #pub.subscribe('datalogger_telemetry', _qs['guiserver_inq'])
    #pub.subscribe('guiserver_telemetry', _qs['guiserver_inq'])
    #pub.subscribe('watchdog_telemetry', _qs['guiserver_inq'])
    # Subscribe to COMMAND messages
    pub.subscribe('dhm_cmd', _qs['controller_inq'])
    # Subscribe to HEARTBEAT messages
    pub.subscribe('heartbeat', _qs['watchdog_inq'])

    ### Create events
    _events = {}
    _events['reconst'] = {}
    _events['reconst']['done'] = ctx.Event()
    _events['controller'] = {}
    _events['controller']['start'] = ctx.Event()

    a = Controller(_qs, pub, _events)
    a.start()
    pub.publish('init_done', interface.InitDonePkt('Reconstructor', 0))
    pub.publish('init_done', interface.InitDonePkt('Framesource', 0))
    pub.publish('init_done', interface.InitDonePkt('Guiserver', 0))
    pub.publish('init_done', interface.InitDonePkt('Datalogger', 0))
    pub.publish('init_done', interface.InitDonePkt('Watchdog', 0))
    count = 0
    _cmdDict = CommandDictionary()
    (cmd, statusstr) = _cmdDict.validate_command('framesource mode=file,exec=run')
    time.sleep(10)
    #_qs['framesource_inq'].put_nowait(interface.Command(cmdobj=cmd))
    while count < 10:
        time.sleep(2)
        print('Count=%d'%(count))
        count += 1

    #pub.publish('rawframe',None)
    _qs['framesource_inq'].put_nowait(None)
    a.join()
