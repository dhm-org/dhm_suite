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
import sys, getopt
import time
import multiprocessing as mp
import numpy as np
import os

def usage(name):
    print('usage: %s [options]'%(name))
    print('  options:')
    print('    -h                Prints usage and exits.')
    print('    -c config_file    Specify config file. Default is ./DEFAULT.ini')

def main(args):
    configFile = os.path.dirname(os.path.realpath(__file__)) + '/DEFAULT.ini'

    #### Parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:")
    except getopt.GetoptError:
        usage(sys.argv[0])
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            usage(sys.argv[0])
            sys.exit()
        elif opt == '-c':
            configFile = arg
            pass
        
    print('ConfigFile = [%s]'%(configFile))

    from . import interface
    from . import dhmpubsub as pubsub
    from .reconstructor import Reconstructor
    from .framesource   import Framesource
    from .guiserver     import Guiserver
    from .controller    import Controller
    from .datalogger    import Datalogger
    from .watchdog      import Watchdog

    ### Create Message Queues
    ctx = mp.get_context('spawn')
    _qs = {}
    _qs['controller_inq']    = ctx.Queue()
    _qs['framesource_inq']   = ctx.Queue()
    _qs['reconstructor_inq'] = ctx.Queue()
    _qs['guiserver_inq']     = ctx.Queue()
    _qs['datalogger_inq']    = ctx.Queue()
    _qs['watchdog_inq']      = ctx.Queue()

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

    ### Create events
    _events = {}
    _events['reconst'] = {}
    _events['reconst']['done'] = ctx.Event()
    _events['controller'] = {}
    _events['controller']['start'] = ctx.Event()

    ### Create components
    _components = {}
    _components['reconstructor'] = Reconstructor(_qs['reconstructor_inq'],pub, _events, configfile=configFile, verbose=False)
    _components['framesource']   = Framesource  (_qs['framesource_inq'], pub, _events, configfile=configFile, verbose=True)
    _components['guiserver']     = Guiserver    (_qs['guiserver_inq'], pub, _events, configfile=configFile, verbose=True)
    _components['datalogger']    = Datalogger   (_qs['datalogger_inq'], pub, _events, configfile=configFile, verbose=True)
    _components['controller']    = Controller   (_qs, pub, _events, configfile=configFile, verbose=True)
    _components['watchdog']      = Watchdog     (_qs['watchdog_inq'], _qs['guiserver_inq'], pub, _events, configfile=configFile, verbose=True)

    ### Start all processes
    for k, v in _components.items():
        v.start()

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
    main(sys.argv[1:])



