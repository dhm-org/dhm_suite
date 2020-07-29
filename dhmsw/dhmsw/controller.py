"""
###############################################################################
#  Copyright 2019, by the California Institute of Technology.
#  ALL RIGHTS RESERVED.
#
#  United States Government Sponsorship acknowledged. Any commercial use
#  must be negotiated with the Office of Technology Transfer at the
#  California Institute of Technology.
#
#  This software may be subject to U.S. export control laws. By accepting
#  this software, the user agrees to comply with all applicable U.S. export
#  laws and regulations. User has the responsibility to obtain export licenses,
#  or other export authority as may be required before exporting such
#  information to foreign countries or providing access to foreign persons.
#
#  file:	controller.py
#  author:	S. Felipe Fregoso
#  brief:	Controls telemetry and signal reconstruction done
#               dispatches commands to executing
#
#
###############################################################################
"""
import sys
import time
import copy
import numpy as np

from . import interface as Iface
from . import telemetry_iface_ag
from . import metadata_classes
from .dhm_cmd_client_server import (DhmCmdServer)
from .dhmcommands import CommandDictionary
from .heartbeat import Heartbeat as HBeat

from .component_abc import ComponentABC

NUMBER_OF_COMPONENTS = 5

class Controller(ComponentABC):
    """
    Controller Component Class
    """
    def __init__(self, identifier, inq, pub, _events, configfile=None, verbose=False):
        ComponentABC.__init__(self,
                              identifier,
                              inq,
                              pub,
                              _events,
                              configfile=configfile,
                              verbose=verbose)

        self._module_init_count = 0
        self._cmd_dict = CommandDictionary()

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

        self._reconst_meta = self._allmeta.metadata['RECONSTRUCTION']
        self._holo_meta = self._allmeta.metadata['HOLOGRAM']
        self._framesource_meta = self._allmeta.metadata['FRAMESOURCE']
        self._datalogger_meta = self._allmeta.metadata['DATALOGGER']
        self._guiserver_meta = self._allmeta.metadata['GUISERVER']
        self._session_meta = self._allmeta.metadata['SESSION']
        self._fouriermask_meta = self._allmeta.metadata['FOURIERMASK']

    def publish_status(self, status_msg=None):
        """
        Publish component status
        """

    def holometa_to_telem(self, meta):
        """
        Convert holo metadata to a telemetry object
        """
        self._holo_telem.set_values(len(meta.wavelength),
                                    meta.wavelength,
                                    meta.dx,
                                    meta.dy,
                                    meta.crop_fraction,
                                    meta.rebin_factor,
                                    meta.bgd_sub,
                                    meta.bgd_file)

        return self._holo_telem.pack()

    def framesourcemeta_to_telem(self, meta):
        """
        Framesource metadata to telemetry object
        """
        self._framesource_telem.set_values(meta.state,
                                           meta.mode,
                                           meta.file['datadir'],
                                           meta.file['currentfile'],
                                           meta.status_msg)

        return self._framesource_telem.pack()

    def dataloggermeta_to_telem(self, meta):
        """
        Datalogger metadata to telemetry object
        """
        self._datalogger_telem.set_values(meta.enabled,
                                          "",
                                          meta.status_msg)

        return self._datalogger_telem.pack()

    def guiservermeta_to_telem(self, meta):
        """
        Gui server metadata to telemetry object
        """
        portlist = [meta.ports['fourier'],\
                    meta.ports['reconst_amp'],\
                    meta.ports['raw_frames'],\
                    meta.ports['telemetry'],\
                   ]

        self._guiserver_telem.set_values(portlist,
                                         meta.connection_status[0:4],
                                         meta.status_msg)

        return self._guiserver_telem.pack()

    def sessionmeta_to_telem(self, meta):
        """
        Session metadata to telemetry object
        """
        self._session_telem.set_values(meta.name,
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
                                       meta.status_msg,
                                      )

        return self._session_telem.pack()

    def fouriermaskmeta_to_telem(self, meta):
        """
        Fourier mask metadata to telemetry object
        """
        x_peak = [circ.get_params[0] for circ in meta.mask.circle_list]
        num_x_peak = len(x_peak)

        y_peak = [circ.get_params[1] for circ in meta.mask.circle_list]
        num_y_peak = len(y_peak)

        mask = np.any(meta.mask.mask, axis=2).flatten()
        self._fouriermask_telem.set_values(num_x_peak,
                                           x_peak,
                                           num_y_peak,
                                           y_peak,
                                           mask,
                                          )

        return self._fouriermask_telem.pack()

    def reconstmeta_to_telem(self, meta):
        """
        Convert reconstruction metadata to telemetry object
        """
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
        """
        Send telemetry to the GUI server component
        """
        msg_pkt = Iface.MessagePkt(Iface.TELEMETRY_TYPE, srcid)
        msg_pkt.append(telem_bin_str)
        msg_pkt.complete_packet()
        gui_pkt = Iface.GuiPacket('telemetry', msg_pkt.to_bytes())
        self._inq['guiserver_inq'].put_nowait(gui_pkt)

    def publish_session_status(self, status_msg=None):
        """
        Publish the session metadata as status
        """
        if status_msg:
            self._session_meta.status_msg = status_msg

        self._pub.publish('session_status',
                          Iface.MetadataPacket(self._session_meta)
                         )

    def process_session_cmd(self, arg):
        """
        Process 'session' commands
        """
        tempsession = copy.copy(self._session_meta)
        tempsession.holo = copy.copy(self._holo_meta)
        validcmd = True

        if not arg: ### Empty parameter list, send reconst status

            self.publish_session_status(status_msg="SUCCESS")

        else:
            for param, value in arg.items():
                if param == 'name':
                    tempsession.name = value
                elif param == 'description':
                    tempsession.description = value
                elif param == 'wavelength':
                    tempsession.holo.wavelength = value
                elif param == 'dx':
                    tempsession.holo.dx = value
                elif param == 'dy':
                    tempsession.holo.dy = value
                elif param == 'crop_fraction':
                    tempsession.holo.crop_fraction = value
                elif param == 'rebin_factor':
                    tempsession.holo.rebin_factor = value
                elif param == 'focal_length':
                    tempsession.lens.focal_length = value
                elif param == 'numerical_aperture':
                    tempsession.lens.numerical_aperture = value
                elif param == 'system_magnification':
                    tempsession.lens.system_magnification = value
                else:
                    validcmd = False

            if validcmd:
                self._session_meta = copy.copy(tempsession)
                self._holo_meta = copy.copy(tempsession.holo)
                # Send holo data to
                self._inq['reconstructor_inq'].put_nowait(self._holo_meta)
                self.publish_session_status(status_msg="SUCCESS")

    def process_shutdown_cmd(self, data):
        """
        Process the shutdown command
        Send 'None' to all component message queues to exit its
        execution loop.
        """
        for _, value in self._inq.items():
            value.put_nowait(None)

    def dispatch_commands(self, modid, data, arg):
        """
        Dispatch the command data to executing component.
        """
        switcher = {
            'reconst':self._inq['reconstructor_inq'].put_nowait,
            'holo':self._inq['reconstructor_inq'].put_nowait,
            'fouriermask':self._inq['reconstructor_inq'].put_nowait,
            'framesource':self._inq['framesource_inq'].put_nowait,
            'guiserver':self._inq['guiserver_inq'].put_nowait,
            'datalogger':self._inq['datalogger_inq'].put_nowait,
            'session':self.process_session_cmd,
            'shutdown':self.process_shutdown_cmd,
        }

        func = switcher.get(modid, None)

        if func == self.process_session_cmd:
            func(arg)
        else:
            func(data)

    def _command_dispatcher(self, data):
        """
        Command Dispatcher.  Sends commands to the assigned component.
        """
        cmd = data.get_cmd()

        for modid, arg in cmd.items():

            if modid in self._cmd_dict.get_dict().keys():

                self.dispatch_commands(modid, data, arg)

            else:
                pass

    def _process_meta(self, data):
        """
        Process the metadata received by the component
        """
        meta = None
        if isinstance(data, Iface.MetadataPacket):
            meta = data.meta
        else:
            meta = data

        if isinstance(meta, metadata_classes.ReconstructionMetadata):
            self._reconst_meta = data.meta
            self.send_telemetry(self.reconstmeta_to_telem(data.meta),
                                Iface.SRCID_TELEMETRY_RECONSTRUCTION,
                               )
        elif isinstance(meta, metadata_classes.FouriermaskMetadata):
            print('Received FouriermaskMetadata')
            self._fouriermask_meta = data.meta
            #self.send_telemetry(self.fouriermaskmeta_to_telem(data.meta),
            #                    Iface.SRCID_TELEMETRY_FOURIERMASK)
        elif isinstance(meta, metadata_classes.SessionMetadata):
            #print('Received SessionMetadata')
            self._session_meta = data.meta
            self.send_telemetry(self.sessionmeta_to_telem(data.meta),
                                Iface.SRCID_TELEMETRY_SESSION,
                               )
        elif isinstance(meta, metadata_classes.HologramMetadata):
            #print('Received HologramMetadata')
            self._holo_meta = data.meta
            self.send_telemetry(self.holometa_to_telem(data.meta),
                                Iface.SRCID_TELEMETRY_HOLOGRAM,
                               )
        elif isinstance(meta, metadata_classes.FramesourceMetadata):
            #print('Received FramesourceMetadata')
            self._framesource_meta = data.meta
            self.send_telemetry(self.framesourcemeta_to_telem(data.meta),
                                Iface.SRCID_TELEMETRY_FRAMESOURCE,
                               )
        elif isinstance(meta, metadata_classes.DataloggerMetadata):
            #print('Received DataloggerMetadata')
            self._datalogger_meta = data.meta
            self.send_telemetry(self.dataloggermeta_to_telem(data.meta),
                                Iface.SRCID_TELEMETRY_DATALOGGER,
                               )
        elif isinstance(meta, metadata_classes.GuiserverMetadata):
            #print('Received GuiserverMetadata')
            self._guiserver_meta = data.meta
            self.send_telemetry(self.guiservermeta_to_telem(data.meta),
                                Iface.SRCID_TELEMETRY_GUISERVER,
                               )
        elif isinstance(meta, metadata_classes.ReconstructionDoneMetadata):
            print("************* RECONST DONE EVENT ***********", time.time())
            self._events['reconst']['done'].set()
        else:
            print('Unknown metadata type')

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

    def _init_for_component_execute(self):
        """
        Intialize variable within run thread
        """
        self._reconst_telem = telemetry_iface_ag.Reconstruction_Telemetry()
        self._session_telem = telemetry_iface_ag.Session_Telemetry()
        self._heartbeat_telem = telemetry_iface_ag.Heartbeat_Telemetry()
        self._holo_telem = telemetry_iface_ag.Hologram_Telemetry()
        self._framesource_telem = telemetry_iface_ag.Framesource_Telemetry()
        self._datalogger_telem = telemetry_iface_ag.Datalogger_Telemetry()
        self._guiserver_telem = telemetry_iface_ag.Guiserver_Telemetry()
        self._fouriermask_telem = telemetry_iface_ag.Fouriermask_Telemetry()

        ### Create heartbeat thread
        ### Start the HBeat thread
    def _process_initdone(self, data):
        """
        Process the "init_done" messages sent by the other components
        """
        if data.get_errorcode() == 0:
            self._module_init_count += 1

        if self._module_init_count >= NUMBER_OF_COMPONENTS:

            self._events['controller']['start'].set()

            if self._cmd_server is None:

                control_q = self._inq['controller_inq']
                validate_func = self._cmd_dict.validate_command
                hostname = self._meta.cmd_hostname
                self._cmd_server = DhmCmdServer(q=control_q,
                                                      validate_func=validate_func,
                                                      hostname=hostname,
                                                      port=self._meta.cmd_port,
                                                     )

            self._cmd_server.start()
            print('Controller: Starting command server...')

    def _process_component_messages(self, data):
        """
        Process the messages received by the component
        """
        if isinstance(data, Iface.InitDonePkt):
            self._process_initdone(data)

        ### Process Metadata Packets by converting them to telemetry
        elif isinstance(data, Iface.MetadataPacket):
            self._process_meta(data)

        elif isinstance(data, Iface.Command):
            print('CONTROLLER: %f: Got command!'%(time.time()))
            ### Dispatch the command to the responsible module
            self._command_dispatcher(data)

        ### Process image (from camera streamer)
        elif isinstance(data, Iface.Image):
            pass

        elif isinstance(data, Iface.ReconstructorProduct):
            print("CONTROLLER: %f: Got reconstructor data!"%(time.time()))

        else:
            print('Controller:  Unknown data type')

    def run(self):
        """
        Component execution loop
        """
        try:
            self._init_for_component_execute()

            self.create_heartbeat()

            self.start_heartbeat()

            print('[%s] Consumer thread started'%(self._id))

            while True:

                data = self._inq['controller_inq'].get()

                if data is None:
                    print('Exiting Controller')
                    break

                self._process_component_messages(data)


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
