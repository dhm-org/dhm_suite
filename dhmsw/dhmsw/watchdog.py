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
#  file:	watchdog.py
#  author:	S. Felipe Fregoso
#  description:	Gets exceptions from modules and reports it in its telemetry
#
###############################################################################
"""
import multiprocessing
import time
import threading
import copy

from . import interface as Iface
from . import telemetry_iface_ag
from . import metadata_classes as MetaC
#from .component_abc import ComponentABC

class WDHeartbeat(threading.Thread):
    """
    Watchdog's Heartbeat Class
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, wdq, ident, data, rate=1.0, cv_timeout=0.01):
        """
        Constructor
        """
        # pylint: disable=too-many-arguments
        if rate <= 0:
            raise ValueError('Rate must be greater than 0')

        threading.Thread.__init__(self)
        self.daemon = True
        self._data = data
        self._cv = threading.Condition()
        self._cv_data_avail = False
        self._wdq = wdq
        self._period = 1.0/rate
        self._cv_timeout = cv_timeout
        self._id = ident

        self._exit = False

    def terminate(self):
        """
        Set exit flag to TRUE to terminal heartbeat thread
        """
        self._exit = True

    def get_update(self):
        """
        Get update of data by checking conditional variable
        """
        isupdate = False
        err_data = self._data

        with self._cv:

            if not self._cv_data_avail:
                self._cv.wait(timeout=self._cv_timeout)

            if self._cv_data_avail:
                err_data = self._data
                self._cv_data_avail = False
                isupdate = True

        return isupdate, err_data

    def set_update(self, data):
        """
        Add data and notify conditional variable
        """
        with self._cv:
            #print('Heartbeat set_update')
            self._data = data
            self._cv_data_avail = True
            self._cv.notify()

    def send_telemetry(self, telem_bin_str, srcid=Iface.SRCID_TELEMETRY_HEARTBEAT):
        """
        Send message to GUI as telemetry
        """
        msg_pkt = Iface.MessagePkt(Iface.TELEMETRY_TYPE, srcid)
        msg_pkt.append(telem_bin_str)
        msg_pkt.complete_packet()
        gui_pkt = Iface.GuiPacket('telemetry', msg_pkt.to_bytes())
        self._wdq.put_nowait(gui_pkt)
        #print('Watchdog:  Sending Heartbeat to GUISERVER')

    def _process_exceptions(self):
        """
        Process the exceptions that were received from the other components
        """
        ### Quickly check condition varible to see if data occured
        _, self._data = self.get_update()
        status_msg = ''
        count = 0
        status = [0, 0, 0, 0, 0]

        ### Process exceptions sent by other componets
        for comp_name, comp_exc in self._data.items():
            if not comp_exc:
                status_msg += 'Process "%s" has not been initialized; '%(comp_name)
                status[count] = int(-1)
            elif comp_exc.exception:
                status_msg += 'Process "%s" has exception [%s]; '\
                              %(comp_name, repr(comp_exc.exception))
                status[count] = int(-1)
            else:
                status[count] = int(0)

            count += 1

        hb_telem = telemetry_iface_ag.Heartbeat_Telemetry()
        hb_telem.set_values(int(time.time()), status, status_msg)
        self.send_telemetry(hb_telem.pack())

    def run(self):
        """
        Watchdog's Heartbeat Execution Loop
        """
        print('[%s] Heartbeat started'%(self._id.upper()))

        while True:

            self._process_exceptions()

            if self._exit:
                break

            time.sleep(self._period)

        print('[%s] Heartbeat thread exit.'%(self._id.upper()))

class Watchdog(multiprocessing.Process):
    """
    Watchdog Component Class
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, inq, outq, pub, _events, configfile=None, verbose=False):
        """
        Constructor
        """
        # pylint: disable=too-many-arguments
        multiprocessing.Process.__init__(self)

        self._verbose = verbose
        self._inq = inq
        self._outq = outq
        self._pub = pub
        self._events = _events

        meta = MetaC.MetadataDictionary(configfile)
        self._meta = meta.metadata['WATCHDOG']

        self._status = {}
        self._status['datalogger'] = None
        self._status['controller'] = None
        self._status['guiserver'] = None
        self._status['reconstructor'] = None
        self._status['framesource'] = None

        self._hbeat = None

    def run(self):
        """
        Components execution Loop
        """
        try:

            inq = self._inq
            outq = self._outq

            self._hbeat = WDHeartbeat(outq, 'watchog', self._status, cv_timeout=.5)

            self._pub.publish('init_done', Iface.InitDonePkt('Watchdog', 0))
            self._events['controller']['start'].wait()

            self._hbeat.start()
            print('Watchdog consumer thread started')

            while True:

                data = inq.get()
                if data is None:
                    print('Exiting Watchdog')
                    break

                ### Process command
                if isinstance(data, Iface.Command):

                    cmd = data.get_cmd()
                    self.process_command(cmd)

                elif isinstance(data, MetaC.HeartbeatMetadata):

                    if data.exception:
                        print('Watchdog: "%s" beat ts=%d, exception=%s'\
                              %(data.ident, int(data.timestamp), 'YES' if data.exception else 'NO'))
                    self._status[data.ident] = data
                    self._hbeat.set_update(self._status)

            self._hbeat.terminate()

        except Exception as err:
            raise err
        finally:
            pass


    def publish_status(self, status_msg=None):
        """
        Publish component status
        """
        if self._verbose:
            print('Watchdog: Publish status')
        if status_msg:
            self._meta.status_msg = status_msg
        self._pub.publish('watchdog_status', Iface.MetadataPacket(self._meta))

    def process_command(self, cmd):
        """
        Process component command
        """
        tmpmeta = copy.copy(self._meta)

        for modid, params in cmd.items():
            if modid == 'watchdog':
                ### Empty parameter list, send status
                if not params:
                    #self._outq.put_nowait(Iface.MetadataPacket(self._meta))
                    self.publish_status(status_msg='SUCCESS')
                    break

                validcmd = True
                for par in params.items():
                    if par == 'dummy_cmd':
                        pass
                    else:
                        validcmd = False

                if validcmd:
                    self._meta = copy.copy(tmpmeta)
                    #self._outq.put_nowait(Iface.MetadataPacket(self._meta))
                    self.publish_status(status_msg='SUCCESS')
