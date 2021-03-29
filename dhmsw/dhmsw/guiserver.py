"""
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
#  file:	guiserver.py
#  author:	S. Felipe Fregoso
#  brief:	Gets raw frames and reconstruction data from other components
#               And sends it to the GUI clients.
#               
#              
###############################################################################
"""
import sys
import time
import queue
import copy
import numpy as np

from . import interface as Iface
from . import telemetry_iface_ag
from . import metadata_classes as MetaC
from .server_client import Server as Svr
from .heartbeat import Heartbeat as HBeat

from .component_abc import ComponentABC

def prepare_raw_img_packet(data):
    """
    Get the raw image from data, serialize it and return as GUI packet
    """
    rawimgpkt = Iface.MessagePkt(Iface.IMAGE_TYPE, Iface.SRCID_IMAGE_RAW)
    rawimage = data.image
    rawimgpkt.append(rawimage)
    rawimgpkt.complete_packet()
    rawb = Iface.GuiPacket('rawframes', rawimgpkt.to_bytes())
    return rawb

def prepare_fourier_img_packet(data):
    """
    Get the fourier image from data, serialize it and return as GUI packet
    """
    fourierpkt = Iface.MessagePkt(Iface.IMAGE_TYPE, Iface.SRCID_IMAGE_FOURIER)
    #fourierimage = data.ft_hologram
    fourierimage = data.get_ft_hologram()
    fourierpkt.append(fourierimage)
    fourierpkt.complete_packet()
    fourier = Iface.GuiPacket('fourier', fourierpkt.to_bytes())
    return fourier

def create_amp_img_pkt(data, img_type, srcid):
    """
    Returns a GUI packet containing the reconstructed amplitude image
    """
    mpkt_a = Iface.MessagePkt(img_type,
                              srcid)
    print("GUISERVER: create_amp_img_pkt(): ", time.time())
    normData = data.reconstwave.amplitude/np.max(data.reconstwave.amplitude) * 255
    mpkt_a.append(normData.astype(dtype=np.uint8))
    mpkt_a.complete_packet()
    amp_image = Iface.GuiPacket('reconst_amp', mpkt_a.to_bytes())
    return amp_image

def create_int_img_pkt(data, img_type, srcid):
    """
    Returns a GUI packet containing the reconstructed intensity image
    """
    mpkt_a = Iface.MessagePkt(img_type,
                              srcid)
    normData = data.reconstwave.intensity/np.max(data.reconstwave.intensity) * 255
    mpkt_a.append(normData.astype(dtype=np.uint8))
    mpkt_a.complete_packet()
    intensity_image = Iface.GuiPacket('reconst_intensity', mpkt_a.to_bytes())
    return intensity_image

def create_phase_img_pkt(data, img_type, srcid):
    """
    Returns a GUI packet containing the reconstructed phase image
    """
    mpkt_a = Iface.MessagePkt(img_type,
                              srcid)
    normData = data.reconstwave.phase/np.max(data.reconstwave.phase) * 255
    mpkt_a.append(normData.astype(dtype=np.uint8))
    mpkt_a.complete_packet()
    phase_image = Iface.GuiPacket('reconst_phase', mpkt_a.to_bytes())
    return phase_image

class Guiserver(ComponentABC):
    """
    GUI Svr Components Class
    """
    def __init__(self, identifier, inq, pub, _events, configfile=None, verbose=False):
        """
        Class initalizer.  Defined in order to add _reconst_meta to method variables.
        """
        ComponentABC.__init__(self,
                              identifier,
                              inq,
                              pub,
                              _events,
                              configfile=configfile,
                              verbose=verbose)
        self._reconst_meta = self._allmeta.metadata['RECONSTRUCTION']

        ### Svr information
        self._servers = {}
        self._servers['reconst_amp'] = None
        self._servers['reconst_intensity'] = None
        self._servers['reconst_phase'] = None
        self._servers['fourier'] = None
        self._servers['rawframes'] = None
        self._servers['telemetry'] = None

    def publish_status(self, status_msg=None):
        """
        Publish component status
        """
        if status_msg:
            self._meta.status_msg = status_msg
        self._pub.publish('guiserver_status', Iface.MetadataPacket(self._meta))



    def process_reconst_product(self, data):
        """
        Process reconstruction component products and send to clients
        """

        print("GUISERVER: Received reconst_product. ", time.time())
        amp_image = None
        intensity_image = None
        phase_image = None
        rawb = None
        fourier = None

        processing_mode = data.reconst_meta.processing_mode

        rawb = prepare_raw_img_packet(data)

        fourier = prepare_fourier_img_packet(data)

        if processing_mode == MetaC.ReconstructionMetadata.RECONST_NONE:
            #print('Recons processing mode = NONE')
            pass
        elif processing_mode == MetaC.ReconstructionMetadata.RECONST_AMP:
            #print('Recons processing mode = AMP')
            amp_image = create_amp_img_pkt(data,
                                           Iface.IMAGE_TYPE,
                                           Iface.SRCID_IMAGE_AMPLITUDE)

        elif processing_mode == MetaC.ReconstructionMetadata.RECONST_INTENSITY:

            #print('Recons processing mode = INTENSITY')
            intensity_image = create_int_img_pkt(data,
                                                 Iface.IMAGE_TYPE,
                                                 Iface.SRCID_IMAGE_INTENSITY)

        elif processing_mode == MetaC.ReconstructionMetadata.RECONST_PHASE:

            #print('Recons processing mode = PHASE')
            phase_image = create_phase_img_pkt(data,
                                               Iface.IMAGE_TYPE,
                                               Iface.SRCID_IMAGE_PHASE)

        elif processing_mode == MetaC.ReconstructionMetadata.RECONST_AMP_AND_PHASE:

            #print('Recons processing mode = RECONST_AMP_AND_PHASE')
            amp_image = create_amp_img_pkt(data,
                                           Iface.IMAGE_TYPE,
                                           Iface.SRCID_IMAGE_AMPLITUDE)
            phase_image = create_phase_img_pkt(data,
                                               Iface.IMAGE_TYPE,
                                               Iface.SRCID_IMAGE_PHASE)

        elif processing_mode == MetaC.ReconstructionMetadata.RECONST_INT_AND_PHASE:

            #print('Recons processing mode = RECONST_INT_AND_PHASE')
            intensity_image = create_int_img_pkt(data,
                                                 Iface.IMAGE_TYPE,
                                                 Iface.SRCID_IMAGE_INTENSITY)
            phase_image = create_phase_img_pkt(data,
                                               Iface.IMAGE_TYPE,
                                               Iface.SRCID_IMAGE_PHASE)

        elif processing_mode == MetaC.ReconstructionMetadata.RECONST_ALL:

            #print('Recons processing mode = ALL')
            amp_image = create_amp_img_pkt(data,
                                           Iface.IMAGE_TYPE,
                                           Iface.SRCID_IMAGE_AMPLITUDE)
            intensity_image = create_int_img_pkt(data,
                                                 Iface.IMAGE_TYPE,
                                                 Iface.SRCID_IMAGE_INTENSITY)
            phase_image = create_phase_img_pkt(data,
                                               Iface.IMAGE_TYPE,
                                               Iface.SRCID_IMAGE_PHASE)


        self.send_images_to_clients(rawb, fourier, amp_image, intensity_image, phase_image)


    def send_images_to_clients(self, rawb, fourier, amp_image, intensity_image, phase_image):
        """
        Send the raw and reconstructed images to all clients
        """
        if rawb:
            self._servers[rawb.servername].send_to_all_clients(rawb.data)

        if fourier:
            self._servers[fourier.servername].send_to_all_clients(fourier.data)

        if amp_image:
            self._servers[amp_image.servername].send_to_all_clients(amp_image.data)

        if intensity_image:
            self._servers[intensity_image.servername].send_to_all_clients(intensity_image.data)

        if phase_image:
            self._servers[phase_image.servername].send_to_all_clients(phase_image.data)

    def process_telemetry_obj(self, data):
        """
        Process telemetry objects received by the component
        """
        telem_type = type(data)
        telem_b = None

        if isinstance(telem_type, telemetry_iface_ag.Hologram_Telemetry):
            msg_pkt = Iface.MessagePkt(Iface.TELEMETRY_TYPE, Iface.SRCID_TELEMETRY_HOLOGRAM)
            msg_pkt.append(data.pack())
            msg_pkt.complete_packet()
            telem_b = Iface.GuiPacket('telemetry', msg_pkt.to_bytes())

        if telem_b:
            print("Guiserver: Sending to [%s] clients"%(telem_b.servername))
            self._servers[telem_b.servername].send_to_all_clients(telem_b.data)

    def process_command(self, data):
        """
        Process commands received by the component
        """
        tempmeta = copy.copy(self._meta)
        cmd = data.get_cmd()
        for modid, var in cmd.items():
            if modid == 'guiserver':
                if not var:
                    self.publish_status("SUCCESS")
                    break
                validcmd = True
                for param, value in var.items():
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
        """
        Get raw image from data, serialize it and send to all clients
        """
        msg_pkt = Iface.MessagePkt(Iface.IMAGE_TYPE, Iface.SRCID_IMAGE_RAW)
        _, image = data.get_img()
        msg_pkt.append(image)
        msg_pkt.complete_packet()
        raw_b = Iface.GuiPacket('rawframes', msg_pkt.to_bytes())
        self._servers[raw_b.servername].send_to_all_clients(raw_b.data)

    def process_metadata(self, data):
        """
        Process metadata and assign to method variable
        """
        if isinstance(data, Iface.MetadataPacket):
            meta = data.meta
        else:
            meta = data

        meta_type = type(meta)

        print("Guiserver: Received meta of type: ", meta_type)
        if meta_type is MetaC.ReconstructionMetadata:
            self._reconst_meta = meta

    def create_image_servers(self):
        """
        Create image servers that will serve the associated images to the connected clients.
        Each image has a server:  Amplitude, Intensity, Phase, Fourier, Raw images, and Telemetry
        """
        self._servers['reconst_amp'] = Svr(self._meta.ports['reconst_amp'],
                                           host=self._meta.hostname,
                                           verbose=True,
                                           timeout=0.1,
                                          )
        self._servers['reconst_intensity'] = Svr(self._meta.ports['reconst_intensity'],
                                                 host=self._meta.hostname,
                                                 verbose=True,
                                                 timeout=0.1,
                                                )
        self._servers['reconst_phase'] = Svr(self._meta.ports['reconst_phase'],
                                             host=self._meta.hostname,
                                             verbose=True,
                                             timeout=0.1,
                                            )
        self._servers['fourier'] = Svr(self._meta.ports['fourier'],
                                       host=self._meta.hostname,
                                       verbose=True,
                                       timeout=0.1,
                                      )
        self._servers['rawframes'] = Svr(self._meta.ports['raw_frames'],
                                         host=self._meta.hostname,
                                         verbose=True,
                                         timeout=0.1,
                                        )
        self._servers['telemetry'] = Svr(self._meta.ports['telemetry'],
                                         host=self._meta.hostname,
                                         verbose=True,
                                         timeout=0.1,
                                        )

    def start_image_servers(self):
        """
        Start running the image servers
        """
        for _, server_obj in self._servers.items():
            server_obj.start()

    def process_component_messages(self, data):
        """
        Process componenet message and determine how to process them
        based on their type
        """


        ### Process command
        if isinstance(data, Iface.Command):
            self.process_command(data)
#                elif isinstance(data, telemetry_iface_ag.Telemetry_Object):
#                    self.process_telemetry_obj(data)
#
        ### Process Reconstruction procduct
        elif isinstance(data, Iface.ReconstructorProduct):
            self.process_reconst_product(data)
#
#                ### Process image (from camera streamer)
        elif isinstance(data, Iface.Image):
            if self._reconst_meta.processing_mode == MetaC.ReconstructionMetadata.RECONST_NONE:
                self.process_image(data)
            #else ## image data should be coming in from the Reconstruction Product type

        elif isinstance(data, Iface.MetadataPacket):
            self.process_metadata(data)

        ### Process image (from camera streamer)
        elif isinstance(data, Iface.GuiPacket):

            #start_time = time.time()
            self._servers[data.servername].send_to_all_clients(data.data)
            #if self._verbose: print('Guiserver received GuiPacket')
        else:
            print('Guiserver received unrecognized type: ', type(data))

    def create_heartbeat(self):
        """
        Create the heartbeat object
        """
        self._hbeat = HBeat(self._pub, self._id.lower())

    def start_heartbeat(self):
        """
        Start the heartbeat
        """
        self._hbeat.start()

    def terminate_heartbeat(self):
        """
        End the execution of this components heartbeat
        """
        self._hbeat.terminate()

    def notify_controller_and_wait(self):
        """
        Notify the controller component that this component is ready
        and wait for controller component OK to start running
        """
        self._pub.publish('init_done', Iface.InitDonePkt('Guiserver', 0))
        print('Guiserver Consumer thread started')

        self._events['controller']['start'].wait()

    def run(self):
        """
        Component execution loop
        """

        try:

            self.create_image_servers()

            self.create_heartbeat()

            self.start_image_servers()

            self.notify_controller_and_wait()

            self.start_heartbeat()

            while True:

                try:
                    data = self._inq.get()
                except queue.Empty:
                    continue

                if data is None:
                    print('Exiting [%s]'%(self._id))
                    break

                self.process_component_messages(data)

            ## End of While
            self.end_component()

        except Exception as err:
            self.handle_component_exception(err)

        finally:
            pass

    def end_component(self):
        """
        End execution of component
        """
        self.terminate_heartbeat()
        if self._hbeat.isAlive():
            self._hbeat.join(timeout=5)
        print('[%s]: End'%(self._id))

    def handle_component_exception(self, err):
        """
        Send Heartbeat error and raise the error
        """
        print('[%s] Exception caught: %s'%(self._id, repr(err)))
        exc_type, exc_obj, t_b = sys.exc_info()
        lineno = t_b.tb_lineno
        print('{} EXCEPTION IN (LINE {}): {}'.format(self._id, lineno, exc_obj))

        self._hbeat.set_update(err)
        if self._hbeat.isAlive():
            self._hbeat.join(timeout=5)
        raise err
