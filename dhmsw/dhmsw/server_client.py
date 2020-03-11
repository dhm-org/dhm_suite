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
#  file:	server_client.py
#  author:	S. Felipe Fregoso
#  description:	Contains classes for server and client objects
###############################################################################
"""
import sys
import select
import socket
import multiprocessing
from threading import Thread
from queue import Queue, Empty

class Client():
    """
    Client class
    """
    def __init__(self, handlerFunc=None):
        """
        Constructor
        """
        self._server = None
        self._port = None
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._readfds = [self._client]
        self._handler_func = handlerFunc

    def get_socket(self):
        """
        Return client socket descriptor
        """
        return self._client

    def connect(self, server, port):
        """
        Connect to the server
        """
        self._server = server
        self._port = port
        self._client.connect((self._server, self._port))
        self._readfds = [self._client]

    def send(self, msg):
        """
        Send data to the server
        """
        self._client.send(msg)

    def recv(self, numbytes):
        """
        Receive data from the server
        """
        return self._client.recv(numbytes)

    def client_thread(self):
        """
        Client thread of execution
        """
        #while True:
        #    readable, writable, errored = select.select(self._readfds, [], [])

    def close(self):
        """
        Close client connection to the server
        """
        self._client.close()


class Server():
    """
    Server Class
    """
    def __init__(self,
                 port,
                 host=socket.gethostname(),
                 maxclients=5,
                 validate_func=None,
                 timeout=None,
                 verbose=False,
                 useprocess=False,
                 enablesend=True,
                ):
        """
        Constructor
        """
        self._host = host
        self._port = port
        self._maxclients = maxclients
        self._verbose = verbose
        self._exit = False
        self._enablesend = enablesend

        self._clients = []
        self._clientthreads = {}
        self._useprocess = useprocess
        if useprocess:
            self._serverthread = multiprocessing.Process(target=self.server_thread)
        else:
            self._serverthread = Thread(target=self.server_thread)
            self._serverthread.daemon = True

        #self._serverthread.daemon = True
        self._timeout = timeout

        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self._server.setblocking(0)
        self._server.bind((self._host, self._port))

        self._readfds = []
        self._writefds = []
        self._validate_func = validate_func

        self._message_queues = {}

        self._sendinprogress = False

    def enable_send(self, ena):
        """
        Enable/disable sending to clients
        """
        self._enablesend = ena

    def send_to_all_clients(self, data):
        """
        Send data to all connected clients
        """
        if self._enablesend:

            for cli in self._clients:

                if self._sendinprogress is False:

                    self._message_queues[cli].put_nowait(data)
                    if cli not in self._writefds:
                        self._writefds.append(cli)
                        #print('Port %d: Add client to writefds'%(self._port))

                else:
                    print('Port %d: SEND is BUSY'%(self._port))
                #if c not in self._writefds:
                #    self._writefds.append(c)
                #    print('Add client to writefds')
        else:
            print('** NOTE Gui server channel is disabled., port=%d'%(self._port))

    def has_clients(self):
        """
        Returns TRUE if there are connected clients
        """
        ret = False
        if len(self._clients) > 0:
            ret = True

        return ret

    def _exit_requested(self):
        """
        Handle exit flag
        """
        if self._verbose:
            print("Port %d: Exiting server: server=%s, port=%s"\
                  %(self._port, self._host, self._port))

        for cli in self._clients:

            self._readfds.remove(cli)

            if cli in self._writefds:
                self._writefds.remove(cli)
                print("Port %d: Removed client from writefs"%(self._port))

            print("Port %d: Removed client from list"%(self._port))
            cli.close()
            self._message_queues[cli].put(None)

    def _accept_client_connections(self, srvr):
        """
        Accept client connections
        """
        if srvr is self._server:
            clientsock, _ = self._server.accept()
            #clientsock.setblocking(0)
            self._readfds.append(clientsock) # Add client socket into readfds list
            self._clients.append(clientsock) # Add client socket into list of clients
            ### Create a queue for each client
            self._message_queues[clientsock] = Queue()
            if self._verbose:
                print("Port %d: Received new client connection"%(self._port))

    def _close_client(self, cli):
        """
        Handle close client connection
        """
        self._readfds.remove(cli)
        if cli in self._writefds:
            self._writefds.remove(cli)
            print("Port %d: Removed client from writefs"%(self._port))
        self._clients.remove(cli)
        print("Port %d: Removed client from list"%(self._port))
        cli.close()
        del self._message_queues[cli]
        print('Port %d: Closed client socket'%(self._port))

    def _handle_client_data(self, sock_r, cli):

        client_had_data = False

        data = None

        if sock_r is cli:  ### Is the socket that has activity one of the clients???
            client_had_data = True

            data = cli.recv(1024)
            ### Client socket CLOSED
            if not data:

                self._close_client(cli)

            else:
                #print('Received from client: %s'%(data))
                #self._message_queues[c].put(data)
                #if c not in self._writefds:
                #    self._writefds.append(c)
                #    print('Add client to writefds')
                pass

        return client_had_data, data

    def server_thread(self):
        """
        Server execution loop
        """
        if self._verbose:
            print('Starting server thread: host=%s, port=%d'%(self._host, self._port))

        self._server.listen(self._maxclients)

        if self._exit:
            return

        self._readfds.append(self._server)

        while True:
            try:
                ### Select: Detect activity in the server and client sockets
                readable,\
                writable,\
                errored = select.select(self._readfds, self._writefds, [], self._timeout)
                if not (readable or writable or errored):
                    ### Timeout
                    if self._exit:

                        self._exit_requested()

                        break

                    continue

                for srvr in readable:

                    self._accept_client_connections(srvr)


                ######################################
                ### Check if clients sent anything
                ######################################
                for cli in self._clients:

                    for sock_r in readable:

                        # At the moment we don't do anything with client data
                        client_had_data, _ = self._handle_client_data(sock_r, cli)
                        if client_had_data:
                            continue

                    for sock_w in writable: ### If sockets available tor writting

                        if sock_w is cli:  ### Is the socket that has activity one of the clients???
                            try:
                                next_msg = self._message_queues[cli].get_nowait()
                                if next_msg is None:
                                    print('next_msg is None')
                                    continue
                            except Empty:
                                #print('Queue is EMPTY')
                                self._writefds.remove(cli)

                            else:
                                self._sendinprogress = True
                                msglen = len(next_msg)

                                totallen = 0
                                #start_time = time.time()
                                while totallen < msglen:
                                    ret = cli.send(next_msg[totallen:])
                                    totallen += ret

                                #print('Port %d Sendall time: %d bytes; %f sec'\
                                #      %(self._port, totallen, time.time()-start_time),\
                                #        time.time(), datetime.datetime.now())
                                #self._writefds.remove(c)
                                self._sendinprogress = False

            except Exception as err:

                exc_type, _, exc_tb = sys.exc_info()
                print("Exception received: %s"%(repr(err)), exc_type, exc_tb.tb_lineno)
                self._sendinprogress = False

        print('Server Threaded Exit.')
        self._server.close()

    def start(self):
        """
        Start the server thread
        """
        self._serverthread.start()

    def exit(self):
        """
        Exit the server thread
        """
        print('Closing server')
        self._exit = True
        self._server.close()

if __name__ == "__main__":
    SERVER = Server(8888, socket.gethostname(), verbose=True)

    SERVER.start()
