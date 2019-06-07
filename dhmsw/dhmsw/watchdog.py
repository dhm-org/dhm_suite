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
import multiprocessing
import time
import threading
from . import interface
from . import telemetry_iface_ag
from . import metadata_classes

class WDHeartbeat(threading.Thread):
    def __init__(self, wdq, ident, data, rate=1.0, cv_timeout=0.01):

        if (rate <= 0 ): raise ValueError('Rate must be greater than 0')

        threading.Thread.__init__(self)
        self.daemon = True
        self._data = data
        self._cv = threading.Condition()
        self._cv_data_avail = False
        self._wdq = wdq
        self._period = 1.0/rate;
        self._cv_timeout = cv_timeout
        self._id = ident

        self._exit = False

    def terminate(self):
        self._exit = True

    def get_update(self):
        isupdate = False
        e = self._data
        with self._cv:
            if not self._cv_data_avail:
                self._cv.wait(timeout=self._cv_timeout)
            if self._cv_data_avail:
                e = self._data
                self._cv_data_avail = False
                isupdate = True

        return isupdate, e

    def set_update(self, data):
        with self._cv:
            #print('Heartbeat set_update')
            self._data = data
            self._cv_data_avail = True
            self._cv.notify()
    
    def send_telemetry(self, telem_bin_str, srcid = interface.SRCID_TELEMETRY_HEARTBEAT):
        a = interface.MessagePkt(interface.TELEMETRY_TYPE, srcid)
        a.append(telem_bin_str)
        a.complete_packet()
        b = interface.GuiPacket('telemetry', a.to_bytes())
        self._wdq.put_nowait(b)
        #print('Watchdog:  Sending Heartbeat to GUISERVER')
        
    def run(self):

        print('IDent = %s'%(self._id))
        print('"%s" Heartbeat started'%(self._id))
        hb_telem = telemetry_iface_ag.Heartbeat_Telemetry()

        while True:
            
            ### Quickly check condition varible to see if data occured
            isupdate, self._data = self.get_update()
            status_msg = ''
            count = 0
            status = [0,0,0,0,0]
            for k,v in self._data.items():
                if not v:
                    status_msg += 'Process "%s" has not been initialized; '%(k)
                    status[count] = int(-1)
                elif v.exception:
                    status_msg += 'Process "%s" has exception [%s]; '%(k, repr(v.exception))
                    status[count] = int(-1)
                else:
                    status[count] = int(0)
                    pass
                count += 1
                    
            hb_telem.set_values(int(time.time()), status, status_msg)
            self.send_telemetry(hb_telem.pack())

            if self._exit: break;
            
            time.sleep(self._period)

        print('"%s" Heartbeat thread exit.'%(self._id))

class Watchdog(multiprocessing.Process):
    def __init__(self, inq, outq, pub, _events, configfile=None, verbose=False):

        multiprocessing.Process.__init__(self)

        self._verbose = verbose
        self._inq = inq
        self._outq = outq
        self._pub = pub
        self._events = _events

        meta = metadata_classes.Metadata_Dictionary(configfile)
        self._meta = meta.metadata['WATCHDOG']

        self._status = {}
        self._status['datalogger'] = None
        self._status['controller'] = None
        self._status['guiserver'] = None
        self._status['reconstructor'] = None
        self._status['framesource'] = None

        self._HB = None

    def run(self):


        try:
            inq = self._inq
            outq = self._outq
    
            self._HB = WDHeartbeat(outq, 'watchog', self._status, cv_timeout=.5)

            self._pub.publish('init_done', interface.InitDonePkt('Watchdog', 0))
            self._events['controller']['start'].wait()

            self._HB.start()
            print('Watchdog consumer thread started')
            while True:
                data = inq.get()
                if data is None:
                    print('Exiting Watchdog')
                    break
    
                ### Process command
                if type(data) is interface.Command:
                    cmd = data.get_cmd()
                    self.process_command(cmd)
                elif type(data) is metadata_classes.Heartbeat_Metadata:
                    if data.exception:
                        print('Watchdog: "%s" beat ts=%d, exception=%s'%(data.ident,int(data.timestamp),'YES' if data.exception else 'NO'))
                    self._status[data.ident] = data;
                    self._HB.set_update(self._status)
            self._HB.terminate()
        except Exception as e:
            raise e
            pass
        finally:
            pass
                 

    def publish_status(self, status_msg=None):
        if self._verbose: print('Watchdog: Publish status')
        if status_msg:
            self._meta.status_msg = status_msg
        self._pub.publish('watchdog_status',interface.MetadataPacket(self._meta))

    def process_command(self, cmd):
        tmpmeta = copy.copy(self._meta)
        for k, v in cmd.items():
            if k == 'watchdog':
                ### Empty parameter list, send status
                if not v:
                    #self._outq.put_nowait(interface.MetadataPacket(self._meta))
                    self.publish_status(status_msg='SUCCESS')
                    break

                validcmd = True
                for param in v.items():
                    if param == 'dummy_cmd':
                        pass
                    else:
                        validcmd = False

                if validcmd:
                    self._meta = copy.copy(tmpmeta)
                    #self._outq.put_nowait(interface.MetadataPacket(self._meta))
                    self.publish_status(status_msg='SUCCESS')


