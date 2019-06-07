import sys, getopt
import time
import multiprocessing as mp
import numpy as np
import os

def usage(name):
    print('usage: %s -h'%(name))

if __name__ == "__main__":

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
