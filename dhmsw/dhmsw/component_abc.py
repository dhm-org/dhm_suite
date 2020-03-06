"""
Abstract class for the dhmsw components

All components should be subclasses of this abstract class
"""
from abc import ABC, abstractmethod
import multiprocessing
from . import metadata_classes

class ComponentABC(ABC, multiprocessing.Process):
    """
    Component abstract class.  All modules that inherit from this class
    will run as a process.
    """

    def __init__(self, identifier, inq, pub, _events, configfile=None, verbose=False):
        """
        Parameters
        -------------
        inq : multiprocessing.queues.Queue
            Queue for input messages into the process.
        pub : dhmpubsub.PubSub
            Handle to the publish/subscribe object
        _events :
            Event to wait for signal indicating reconstruct of an image has completed
        verbose : boolean
            If TRUE print detail information to terminal, FALSE otherwise.
        """

        multiprocessing.Process.__init__(self)

        self._id = identifier.upper()
        self._verbose = verbose
        #### Create the consumer thread for this module
        self._inq = inq
        self._events = _events
        self._pub = pub

        self._allmeta = metadata_classes.MetadataDictionary(configfile)
        self._meta = self._allmeta.metadata[self._id]
        self._hbeat = None

    @abstractmethod
    def publish_status(self, status_msg=None):
        """
        Function used to publish status of the component
        It is abstract so that components are forced to implement
        """
        while False:
            yield None

    @abstractmethod
    def run(self):
        """
        Component run function
        """
        while False:
            yield None
