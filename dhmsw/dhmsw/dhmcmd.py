#!/usr/local/bin/python3
import sys
import socket 

from .dhm_cmd_client_server import (DHM_Command_Client)

HOST=socket.gethostbyname('localhost')
PORT = 10000

def usage():
    pass

def dhm_command(server, port, cmdstr):

    a = DHM_Command_Client(server, port)
    return a.send(cmdstr)

if __name__ == '__main__':
    ### Ensure input parameters are more than 1
    if len(sys.argv) < 2:
        print("Error.  At least one input parameter must be given")
        usage()
        exit(-1)

    ### Get every thing after the script name as command
    cmd = str(" ".join(sys.argv[1:]))
    dhm_command(server=HOST, port=PORT, cmdstr=cmd)

    




