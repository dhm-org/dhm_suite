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
#  file:	framesource.py
#  author:	S. Felipe Fregoso
#  description:	Python application to send a command to DHM command server
#
###############################################################################
"""
import sys
import socket

from .dhm_cmd_client_server import (DhmCmdClient)

HOST = socket.gethostbyname('localhost')
PORT = 10000

def usage():
    """
    Print Usage
    """

def dhm_command(server, port, cmdstr):
    """
    Send a DHM command by establishing connection to the
    DHM command server as a client and sending the command.
    """
    cmd_cli = DhmCmdClient(server, port)
    return cmd_cli.send(cmdstr)

if __name__ == '__main__':
    ### Ensure input parameters are more than 1
    if len(sys.argv) < 2:
        print("Error.  At least one input parameter must be given")
        usage()
        sys.exit()

    ### Get every thing after the script name as command
    CMD = str(" ".join(sys.argv[1:]))
    dhm_command(server=HOST, port=PORT, cmdstr=CMD)
