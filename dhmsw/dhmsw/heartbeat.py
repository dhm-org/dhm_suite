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
#  file:	heartbeat.py
#  author:	S. Felipe Fregoso
#  description:	Heartbeat thread that send aliveness status of caller
#
###############################################################################
"""
import threading
import time
from .metadata_classes import HeartbeatMetadata

class Heartbeat(threading.Thread):
    """
    Hearbeat Thread Class
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, pub, ident, rate=1.0, cv_timeout=0.01):

        if rate <= 0:
            raise ValueError('Rate must be greater than 0')

        threading.Thread.__init__(self)
        #self.daemon = True
        self._cv = threading.Condition()
        self._cv_data_avail = False
        #self._wdq = wdq
        self._pub = pub
        self._period = 1.0/rate
        self._cv_timeout = cv_timeout
        self._id = ident
        self._exception = None

        self._exit = False

    def terminate(self):
        """
        Sets the exit flag to True to terminate the heartbeat thread
        """
        self._exit = True

    def get_update(self):
        """
        Retrieve the last error event sent to heartbeat
        """
        isupdate = False
        err = None
        with self._cv:
            if not self._cv_data_avail:
                self._cv.wait(timeout=self._cv_timeout)
            if self._cv_data_avail:
                err = self._exception
                self._cv_data_avail = False
                isupdate = True

        return isupdate, err

    def set_update(self, exception):
        """
        Update the error exception
        """
        with self._cv:
            #print('Heartbeat set_update')
            self._exception = exception
            self._cv_data_avail = True
            self._cv.notify()

    def run(self):
        """
        Execution loop of the heartbeat thread
        """
        hb_meta = HeartbeatMetadata()
        hb_meta.ident = self._id

        print('[%s] Heartbeat started'%(self._id))
        while True:

            ### Quickly check condition varible to see if exception occured
            _exit, err = self.get_update()
            hb_meta.timestamp = time.time()
            hb_meta.exception = err

            #self._wdq.put(hb_meta)
            self._pub.publish('heartbeat', hb_meta)

            if _exit or self._exit:
                break

            time.sleep(self._period)

        print('[%s] Heartbeat thread exit.'%(self._id))
