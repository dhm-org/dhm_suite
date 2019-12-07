from abc import ABC, abstractmethod
import multiprocessing
from . import metadata_classes

class ComponentABC(ABC, multiprocessing.Process):

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

        self._allmeta = metadata_classes.Metadata_Dictionary(configfile)
        self._meta = self._allmeta.metadata[self._id]
        self._HB = None

        self.initialize_component()
        pass

    @abstractmethod
    def initialize_component(self):
        """ Function to initialized component specific stuff.  This is called by the __init__ """
        while False:
            yield None

    @abstractmethod
    def publish_status(self):
        while False:
            yield None

    @abstractmethod
    def run(self):
        while False:
            yield None

    pass
