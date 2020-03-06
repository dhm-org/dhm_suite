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
#  file:	main.py
#  author:	S. Felipe Fregoso
#  description:	Entry point for the dhmsw application
#
###############################################################################
"""
import os
import sys
import getopt
import multiprocessing as mp

from .reconstructor import Reconstructor
from .framesource   import Framesource
from .guiserver     import Guiserver
from .controller    import Controller
from .datalogger    import Datalogger
from .watchdog      import Watchdog
from . import dhmpubsub as pubsub

def usage(name):
    """
    Print usage
    """
    print('usage: %s [options]'%(name))
    print('  options:')
    print('    -h                Prints usage and exits.')
    print('    -c config_file    Specify config file. Default is ./DEFAULT.ini')

def create_message_queues(ctx):
    """
    Create message queues to be used by components
    """
    ### Create Message Queues
    ctx = mp.get_context('spawn')
    _qs = {}
    _qs['controller_inq'] = ctx.Queue()
    _qs['framesource_inq'] = ctx.Queue()
    _qs['reconstructor_inq'] = ctx.Queue()
    _qs['guiserver_inq'] = ctx.Queue()
    _qs['datalogger_inq'] = ctx.Queue()
    _qs['watchdog_inq'] = ctx.Queue()

    return _qs

def make_pubsub_connections(_qs):
    """
    Make the publish subscribe connections
    """
    ### Make the publish/subscribe connections
    pub = pubsub.PubSub()

    #published by all modules to indicate that it is done initializing
    pub.subscribe('init_done', _qs['controller_inq'])

    # Subscribe to RAW FRAMES
    pub.subscribe('rawframe', _qs['guiserver_inq'])
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

    return pub

def create_events(ctx):
    """
    Create events
    """
    _events = {}
    _events['reconst'] = {}
    _events['reconst']['done'] = ctx.Event()
    _events['controller'] = {}
    _events['controller']['start'] = ctx.Event()

    return _events

def create_communication_ports():
    """
    Create communiction ports used by the components to
    communicate between each other
    """
    ctx = mp.get_context('spawn')

    # Create Message Queues
    _qs = create_message_queues(ctx)

    # Create Publish/Subscribe connections
    pub = make_pubsub_connections(_qs)

    ### Create events
    _events = create_events(ctx)

    return (_qs, pub, _events)

def create_components(pub, _qs, _events, config_file):
    """
    Create components and return them in dictionary
    """

    _components = {}
    _components['reconstructor'] = Reconstructor(_qs['reconstructor_inq'],
                                                 pub,
                                                 _events,
                                                 configfile=config_file,
                                                 verbose=False
                                                )
    _components['framesource'] = Framesource("framesource",
                                             _qs['framesource_inq'],
                                             pub,
                                             _events,
                                             configfile=config_file,
                                             verbose=True
                                            )
    _components['guiserver'] = Guiserver("guiserver",
                                         _qs['guiserver_inq'],
                                         pub,
                                         _events,
                                         configfile=config_file,
                                         verbose=True
                                        )
    _components['datalogger'] = Datalogger("datalogger",
                                           _qs['datalogger_inq'],
                                           pub, _events,
                                           configfile=config_file,
                                           verbose=True
                                          )
    _components['controller'] = Controller("controller",
                                           _qs,
                                           pub,
                                           _events,
                                           configfile=config_file,
                                           verbose=True
                                          )
    _components['watchdog'] = Watchdog(_qs['watchdog_inq'],
                                       _qs['guiserver_inq'],
                                       pub,
                                       _events,
                                       configfile=config_file,
                                       verbose=True
                                      )
    return _components

def main():
    """
    Main entry point
    """
    config_file = os.path.dirname(os.path.realpath(__file__)) + '/DEFAULT.ini'

    #### Parse command line options
    try:

        opts, _ = getopt.getopt(sys.argv[1:], "hc:")

    except getopt.GetoptError:

        usage(sys.argv[0])
        sys.exit(2)

    for opt, arg in opts:

        if opt == '-h':

            usage(sys.argv[0])
            sys.exit()

        elif opt == '-c':

            config_file = arg

    print('ConfigFile = [%s]'%(config_file))

    # Create communication ports
    _qs, pub, _events = create_communication_ports()

    ### Create components
    _components = create_components(pub, _qs, _events, config_file)

    ### Start executing all components
    for _, comp in _components.items():
        comp.start()

    ### Wait for each component to complete its execution.
    _components['reconstructor'].join()
    print('reconstructed ENDED')
    _components['framesource'].join()
    print('framesource ENDED')
    _components['guiserver'].join()
    print('guiserver ENDED')
    _components['datalogger'].join()
    print('datalogger ENDED')
    _components['controller'].join()
    print('controller ENDED')
    _components['watchdog'].join()
    print('watchdog ENDED')

    print('End of main')

if __name__ == "__main__":
    main()
