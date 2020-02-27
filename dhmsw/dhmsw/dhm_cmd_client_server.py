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
#  file:	dhm_cmd_client_server.py
#  author:	S. Felipe Fregoso
#  description:	Classes for creating a DHM client and server
#
###############################################################################
"""
import socket
import select
import threading
from . import interface

class DhmCmdClient():
    """ DHM Command Client
        Connect to the server, send the command string, then wait for a reply
        Raises exception if error connecting or timeout receiving command
    """
    def __init__(self, server='localhost', port=10000):
        """
        Constructor
        """
        self._server = server
        self._port = port
        self._sock = None

    def get_sock(self):
        """
        Return the socket handle
        """
        return self._sock

    def get_port(self):
        """
        Return the port
        """
        return self._port

    def get_server(self):
        """
        Return the server name
        """
        return self._server

    def send(self, cmdstr):
        """
        Send command string to client

        Make a connection to the server, sends the command, waits for response,
        then closes the socket connections.
        """
        try:
            ### Create socket
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(2)

            ### Connect to server
            self._sock.connect((self._server, self._port))

            ### Send command string
            self._sock.send(cmdstr.encode())

            ### Wait for return acknowledment
            reply = self._sock.recv(1024)
            print(reply.decode())
            ### Close socket
            self._sock.close()
            self._sock = None

            ### Display return string
            return reply

        except socket.error as err:
            print('%s'%(repr(err)))
            if self._sock:
                self._sock.close()
                self._sock = None
            raise err

class DhmCmdServer(threading.Thread):
    """
    Class for DHM Command Server
    """
    # pylint: disable=too-many-instance-attributes
    # Eleven is reasonable in this case
    def __init__(self,
                 hostname='localhost',
                 port=10000,
                 q=None,
                 validate_func=None,
                 blocking=False,
                ):
        """
        Constructor
        """
        # pylint: disable=too-many-arguments
        # Six arguments are ok in this case
        self._q = q
        self._blocking = blocking
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if not self._blocking:
            self._server.setblocking(0)

        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._host = socket.gethostbyname(hostname)
        self._port = port
        self._maxclients = 5
        self._server.bind((self._host, self._port))
        self._clients = []

        threading.Thread.__init__(self)

        self.daemon = True
        self._timeout = 1
        self._readfds = [self._server]
        self._validate_func = validate_func

    def _accept_client(self, rsock):
        """
        Accept client connection
        """
        if rsock is self._server: # Accept new connections

            clientsock, _ = self._server.accept()
            if not self._blocking:
                clientsock.setblocking(0)
            self._readfds.append(clientsock)
            self._clients.append(clientsock)

    def _receive_and_reply(self, rsock, cli):
        """
        Receive data from client, and reply with acknowledgment.

        Close the client socket if connection lost
        """
        client_match = True
        if rsock is cli:
            cmd_line = cli.recv(1024)
            print("Received: [%s]"%(cmd_line.decode()))
            if not cmd_line: #Socket closed
                self._readfds.remove(cli)
                self._clients.remove(cli)
                cli.close()
                print('Closed client socket')
            else:
                if self._q:
                    if self._validate_func:
                        (cmd, statusstr) = self._validate_func(cmd_line.decode())
                        if cmd:
                            replystr = "ACK: %s"%(statusstr)
                            self._q.put_nowait(interface.Command(cmdobj=cmd))
                            cli.send(replystr.encode())
                        else:
                            replystr = "ERR: %s"%(statusstr)
                            cli.send(replystr.encode())
                    else:
                        self._q.put_nowait(cmd_line.decode())
                        cli.send("ACK".encode())
        else:
            client_match = False

        return client_match

    def run(self):
        """
        Server execution thread
        """
        self._server.listen(self._maxclients)
        while True:
            try:
                readable, writable, errored = select.select(self._readfds, [], [])
                if not (readable or writable or errored):
                    ### Timeout
                    continue
                for rsock in readable:

                    self._accept_client(rsock)

                for cli in self._clients: # Check if clients sent anything

                    for rsock in readable:

                        client_match = self._receive_and_reply(rsock, cli)
                        if client_match:
                            continue


            except Exception as err:
                self._server.close()
                #if self._q:
                #    self._q.put(None)
                raise err

    def exit(self):
        """
        Exit server
        """
        self._server.close()
