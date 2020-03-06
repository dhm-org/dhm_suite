"""
  Data Logger Component

  Description:  Data logger component logs to non-volatile messages received.

"""
import copy
#import time
from . import interface
#from . import metadata_classes
from . import heartbeat

from .component_abc import ComponentABC

class Datalogger(ComponentABC):
    """
    Data logger class component
    """

    def run(self):
        try:
            inq = self._inq

            print("PID", self.pid)
            ### Create heartbeat thread
            self._hbeat = heartbeat.Heartbeat(self._pub, 'datalogger')

            self._pub.publish('init_done', interface.InitDonePkt('Datalogger', 0))
            self._events['controller']['start'].wait()
            ### Start the Heartbeat thread
            self._hbeat.start()
            print('Datalogger consumer thread started')
            while True:
                data = inq.get()
                if data is None:
                    print('Exiting Datalogger')
                    break

                ### Process command
                if isinstance(data, interface.Command):
                    cmd = data.get_cmd()
                    self.process_command(cmd)
            ## End of While
            self._hbeat.terminate()

        except Exception as err:
            print('Datalogger Exception caught: %s'%(repr(err)))
            # Store exception and notify the heartbeat thread
            self._hbeat.set_update(err)

            # Wait for heartbeat thread to return
            if self._hbeat.isAlive():
                print('Heartbeat is ALIVE')
                self._hbeat.join(timeout=5)

            ## Die!
            raise err
        finally:
            pass

    def publish_status(self, status_msg=None):
        if status_msg:
            self._meta.status_msg = status_msg
        self._pub.publish('datalogger_status', interface.MetadataPacket(self._meta))

    def process_command(self, cmd):
        """
        Process commands for this component
        """
        tmpmeta = copy.copy(self._meta)
        for modid, var in cmd.items():
            if modid == 'datalogger':
                ### Empty parameter list, send status
                if not var:
                    self.publish_status(status_msg='SUCCESS')
                    break

                validcmd = True
                #raise ValueError('Intentional error')
                for param in var.items():
                    if param == 'enabled':
                        pass
                    elif param == 'rootpath':
                        pass
                    else:
                        validcmd = False

                if validcmd:
                    self._meta = copy.copy(tmpmeta)
                    self.publish_status(status_msg='SUCCESS')
