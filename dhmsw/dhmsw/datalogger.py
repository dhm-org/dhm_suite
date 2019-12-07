import copy
import multiprocessing
import time
from . import interface
from . import metadata_classes 
from . import heartbeat

from .component_abc import ComponentABC

class Datalogger(ComponentABC):
#    def __init__(self, inq, pub, _events, configfile=None, verbose=False):
#
#        multiprocessing.Process.__init__(self)
#
#        self._verbose = verbose
#        self._inq = inq
#        self._pub = pub
#        self._events = _events
#
#        meta = metadata_classes.Metadata_Dictionary(configfile)
#        self._meta = meta.metadata['DATALOGGER']
#
#        ### Heartbeat must be created from run
#        self._HB = None
#
#        #self._hb_thread.daemon = True

    def initialize_component(self):
        pass

    def run(self):
        try:
            inq = self._inq

            print("PID", self.pid)
            ### Create heartbeat thread
            self._HB = heartbeat.Heartbeat(self._pub, 'datalogger')
    
            self._pub.publish('init_done', interface.InitDonePkt('Datalogger', 0))
            self._events['controller']['start'].wait()
            ### Start the Heartbeat thread
            self._HB.start()
            print('Datalogger consumer thread started')
            while True:
                data = inq.get()
                if data is None:
                    print('Exiting Datalogger')
                    break
    
                ### Process command
                if type(data) is interface.Command:
                    cmd = data.get_cmd()
                    self.process_command(cmd)
            ## End of While
            self._HB.terminate()

        except Exception as e:
            print('Datalogger Exception caught: %s'%(repr(e)))
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
    
    def publish_status(self, status_msg=None):
        if status_msg:
            self._meta.status_msg = status_msg
        self._pub.publish('datalogger_status',interface.MetadataPacket(self._meta))

    def process_command(self, cmd):
        tmpmeta = copy.copy(self._meta)
        for k, v in cmd.items():
            if k == 'datalogger':
                ### Empty parameter list, send status
                if not v:
                    self.publish_status(status_msg='SUCCESS')
                    break

                validcmd = True
                raise ValueError('Intentional error')
                for param in v.items():
                    if param == 'enabled':
                        pass
                    elif param == 'rootpath':
                        pass
                    else:
                        validcmd = False

                if validcmd:
                    self._meta = copy.copy(tmpmeta)
                    self.publish_status(status_msg='SUCCESS')


