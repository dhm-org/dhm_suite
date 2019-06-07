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
from .server_client import Server
from .heartbeat import Heartbeat

class Guiserver(multiprocessing.Process):
    def __init__(self, inq, pub, _events, configfile=None, verbose=False):


        multiprocessing.Process.__init__(self)
        self.daemon = True

        self._verbose = verbose

        meta = metadata_classes.Metadata_Dictionary(configfile)
        self._meta = meta.metadata['GUISERVER']
        self._reconst_meta = meta.metadata['RECONSTRUCTION']

        #### Create the consumer thread for this module
        self._inq = inq
        self._pub = pub
        self._events = _events

        self._HB = None

        ### Server information
        self._servers = {}
        self._servers['reconst_amp'] = None
        self._servers['reconst_intensity'] = None
        self._servers['reconst_phase'] = None
        self._servers['fourier'] = None
        self._servers['rawframes'] = None
        self._servers['telemetry'] = None


    def publish_status(self, status_msg = None):
        if status_msg:
            self._meta.status_msg = status_msg
        self._pub.publish('guiserver_status', interface.MetadataPacket(self._meta))
        
    def process_reconst_product(self, data):

        amp_image = None
        intensity_image = None
        phase_image = None
        rawb = None
        fourier = None

        ### Prepare Raw Frame Packet for GUI display
        rawimgpkt = interface.MessagePkt(interface.IMAGE_TYPE, interface.SRCID_IMAGE_RAW)
        rawimage = data.image
        rawimgpkt.append(rawimage)
        rawimgpkt.complete_packet()
        rawb = interface.GuiPacket('rawframes', rawimgpkt.to_bytes())

        ### Prepare Fourier Image Packet for GUI display
        fourierpkt = interface.MessagePkt(interface.IMAGE_TYPE, interface.SRCID_IMAGE_FOURIER)
        #fourierimage = np.log(np.abs(data.hologram.ft_hologram)) # Log of the magnitude
        #fourierimage = np.log(np.abs(data.ft_hologram)) # Log of the magnitude
        fourierimage = data.ft_hologram
        fourierpkt.append(fourierimage)
        #fourierpkt.append(fourierimage.astype(dtype=np.uint8))
        fourierpkt.complete_packet()
        fourier = interface.GuiPacket('fourier', fourierpkt.to_bytes())
        
        if data.reconst_meta.processing_mode == metadata_classes.Reconstruction_Metadata.RECONST_NONE:
            #print('Recons processing mode = NONE')
            pass
        elif data.reconst_meta.processing_mode == metadata_classes.Reconstruction_Metadata.RECONST_AMP:
            #print('Recons processing mode = AMP')
            a = interface.MessagePkt(interface.IMAGE_TYPE, interface.SRCID_IMAGE_AMPLITUDE)
            a.append(data.reconstwave.amplitude.astype(dtype=np.uint8))
            a.complete_packet()
            amp_image = interface.GuiPacket('reconst_amp', a.to_bytes())
            pass
        elif data.reconst_meta.processing_mode == metadata_classes.Reconstruction_Metadata.RECONST_INTENSITY:
            #print('Recons processing mode = INTENSITY')
            a = interface.MessagePkt(interface.IMAGE_TYPE, interface.SRCID_IMAGE_INTENSITY)
            a.append(data.reconstwave.intensity.astype(dtype=np.uint8))
            a.complete_packet()
            intensity_image = interface.GuiPacket('reconst_intensity', a.to_bytes())
        elif data.reconst_meta.processing_mode == metadata_classes.Reconstruction_Metadata.RECONST_PHASE:
            #print('Recons processing mode = PHASE')
            a = interface.MessagePkt(interface.IMAGE_TYPE, interface.SRCID_IMAGE_PHASE)
            a.append(data.reconstwave.phase.astype(dtype=np.uint8))
            a.complete_packet()
            phase_image = interface.GuiPacket('reconst_phase', a.to_bytes())
        elif data.reconst_meta.processing_mode == metadata_classes.Reconstruction_Metadata.RECONST_AMP_AND_PHASE:
            a = interface.MessagePkt(interface.IMAGE_TYPE, interface.SRCID_IMAGE_AMPLITUDE)
            a.append(data.reconstwave.amplitude.astype(dtype=np.uint8))
            a.complete_packet()
            amp_image = interface.GuiPacket('reconst_amp', a.to_bytes())
            b = interface.MessagePkt(interface.IMAGE_TYPE, interface.SRCID_IMAGE_PHASE)
            b.append(data.reconstwave.phase.astype(dtype=np.uint8))
            b.complete_packet()
            phase_image = interface.GuiPacket('reconst_phase', b.to_bytes())
            #print('Recons processing mode = RECONST_AMP_AND_PHASE')
        elif data.reconst_meta.processing_mode == metadata_classes.Reconstruction_Metadata.RECONST_INT_AND_PHASE:
            a = interface.MessagePkt(interface.IMAGE_TYPE, interface.SRCID_IMAGE_INTENSITY)
            a.append(data.reconstwave.intensity.astype(dtype=np.uint8))
            a.complete_packet()
            intensity_image = interface.GuiPacket('reconst_intensity', a.to_bytes())
            b = interface.MessagePkt(interface.IMAGE_TYPE, interface.SRCID_IMAGE_PHASE)
            b.append(data.reconstwave.phase.astype(dtype=np.uint8))
            b.complete_packet()
            phase_image = interface.GuiPacket('reconst_phase', b.to_bytes())
            #print('Recons processing mode = RECONST_INT_AND_PHASE')
        elif data.reconst_meta.processing_mode == metadata_classes.Reconstruction_Metadata.RECONST_ALL:
            a = interface.MessagePkt(interface.IMAGE_TYPE, interface.SRCID_IMAGE_AMPLITUDE)
            a.append(data.reconstwave.amplitude.astype(dtype=np.uint8))
            a.complete_packet()
            amp_image = interface.GuiPacket('reconst_amp', a.to_bytes())
            b = interface.MessagePkt(interface.IMAGE_TYPE, interface.SRCID_IMAGE_INTENSITY)
            b.append(data.reconstwave.intensity.astype(dtype=np.uint8))
            b.complete_packet()
            intensity_image = interface.GuiPacket('reconst_intensity', b.to_bytes())
            c = interface.MessagePkt(interface.IMAGE_TYPE, interface.SRCID_IMAGE_PHASE)
            c.append(data.reconstwave.phase.astype(dtype=np.uint8))
            c.complete_packet()
            phase_image = interface.GuiPacket('reconst_phase', c.to_bytes())
            #print('Recons processing mode = ALL')

        if rawb: self._servers[rawb.servername].send_to_all_clients(rawb.data)
        if fourier: self._servers[fourier.servername].send_to_all_clients(fourier.data)
        if amp_image: self._servers[amp_image.servername].send_to_all_clients(amp_image.data)
        if intensity_image: self._servers[intensity_image.servername].send_to_all_clients(intensity_image.data)
        if phase_image: self._servers[phase_image.servername].send_to_all_clients(phase_image.data)

    def process_telemetry_obj(self, data):
        telem_type = type(data)
        b = None
        if telem_type is telemetry_iface_ag.Hologram_Telemetry:
            a = interface.MessagePkt(interface.TELEMETRY_TYPE, interface.SRCID_TELEMETRY_HOLOGRAM)
            a.append(data.pack())
            a.complete_packet()
            b = interface.GuiPacket('telemetry', a.to_bytes())

        if b:
            print("Guiserver: Sending to [%s] clients"%(b.servername))
            self._servers[b.servername].send_to_all_clients(b.data)
            pass

    def process_command(self, data):
        tempmeta = copy.copy(self._meta)
        cmd = data.get_cmd()
        for k, v in cmd.items():
            if k == 'guiserver':
                if not v:
                    self.publish_status("SUCCESS")
                    break
                validcmd = True
                for param, value in v.items():
                    if param == 'enable_rawframes':
                        tempmeta.enabled[param] = value
                        self._servers['rawframes'].enable_send(value)
                    elif param == 'enable_fourier':
                        tempmeta.enabled[param] = value
                        self._servers['fourier'].enable_send(value)
                    elif param == 'enable_amplitude':
                        tempmeta.enabled[param] = value
                        self._servers['reconst_amp'].enable_send(value)
                    elif param == 'enable_intensity':
                        tempmeta.enabled[param] = value
                        self._servers['reconst_intensity'].enable_send(value)
                    elif param == 'enable_phase':
                        tempmeta.enabled[param] = value
                        self._servers['reconst_phase'].enable_send(value)
                    else:
                        validcmd = False
                        self.publish_status("ERROR. Unknown parameter [%s]"%(param))
                if validcmd:
                    self._meta = copy.copy(tempmeta)
                    self.publish_status("SUCCESS")
         
    def process_image(self, data):
        a = interface.MessagePkt(interface.IMAGE_TYPE, interface.SRCID_IMAGE_RAW)
        meta, image = data.get_img()
        a.append(image)
        a.complete_packet()
        b = interface.GuiPacket('rawframes', a.to_bytes())
        self._servers[b.servername].send_to_all_clients(b.data)

    def process_metadata(self, data):
        if type(data) is interface.MetadataPacket:
            meta = data.meta
        else:
            meta = data

        meta_type = type(meta)

        print("Guiserver: Received meta of type: ", meta_type)
        if meta_type is metadata_classes.Reconstruction_Metadata:
            self._reconst_meta = meta

    def run(self):

        try:
            self._servers['reconst_amp'] = Server(self._meta.ports['reconst_amp'], host=self._meta.hostname, verbose=True,timeout=0.1)
            self._servers['reconst_intensity'] = Server(self._meta.ports['reconst_intensity'], host=self._meta.hostname, verbose=True,timeout=0.1)
            self._servers['reconst_phase'] = Server(self._meta.ports['reconst_phase'], host=self._meta.hostname, verbose=True,timeout=0.1)
            self._servers['fourier'] = Server(self._meta.ports['fourier'], host=self._meta.hostname, verbose=True, timeout=0.1)
            self._servers['rawframes'] = Server(self._meta.ports['raw_frames'], host=self._meta.hostname, verbose=True, timeout=0.1)
            self._servers['telemetry'] = Server(self._meta.ports['telemetry'], host=self._meta.hostname, verbose=True, timeout=0.1)

            ### Create heartbeat thread
            ### Start the Heartbeat thread
            self._HB = Heartbeat(self._pub, 'guiserver')
    
            ### Startup the GUI servers
            for k, v in self._servers.items():
                v.start()
    
            self._pub.publish('init_done', interface.InitDonePkt('Guiserver', 0))
            print('Guiserver Consumer thread started')

            self._events['controller']['start'].wait()
            self._HB.start()
            while True:
                try:
                    data = self._inq.get()
                except queue.Empty as e:
                    continue
                datatype = type(data)
                if self._verbose: 
                    if self._inq.qsize() > 0: print('QSize = %d'%(self._inq.qsize()), datatype)
                if data is None:
                    print('Exiting Guiserver')
                    break
#    
#                ### Process command
                if datatype is interface.Command:
                    self.process_command(data)
                    pass
#                elif isinstance(data, telemetry_iface_ag.Telemetry_Object):
#                    self.process_telemetry_obj(data)
#    
                ### Process Reconstruction procduct
                elif datatype is interface.ReconstructorProduct:
                    self.process_reconst_product(data)
                    pass
#
#                ### Process image (from camera streamer)
                elif datatype is interface.Image:
                    if self._reconst_meta.processing_mode == metadata_classes.Reconstruction_Metadata.RECONST_NONE:
                        self.process_image(data)
                    #else ## image data should be coming in from the Reconstruction Product type
    
                elif isinstance(data, interface.MetadataPacket):
                    self.process_metadata(data)

                ### Process image (from camera streamer)
                elif datatype is interface.GuiPacket:
    
                    start_time = time.time()
                    self._servers[data.servername].send_to_all_clients(data.data)
                    #if self._verbose: print('Guiserver received GuiPacket')
                    pass
                else:
                    print('Guiserver received unrecognized type: ',type(data))

            ## End of While
            self._HB.terminate()
        except Exception as e:
            print('GuiServer Exception caught: %s'%(repr(e)))
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

    a = Guiserver(_qs['guiserver_inq'], pub, _events)
    a.start()
    _events['controller']['start'].set() ## Mimic the Controller
    count = 0
    _cmdDict = CommandDictionary()
    (cmd, statusstr) = _cmdDict.validate_command('guiserver enable_amplitude=true')
    time.sleep(10)
    _qs['guiserver_inq'].put_nowait(interface.Command(cmdobj=cmd))
    while count < 10:
        time.sleep(2)
        print('Count=%d'%(count))
        count += 1

    #pub.publish('rawframe',None)
    _qs['guiserver_inq'].put_nowait(None)
    a.join()
