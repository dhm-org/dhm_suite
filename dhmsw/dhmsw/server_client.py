import sys
import time
import datetime
import select
import socket
from threading import Thread
import multiprocessing
from queue import Queue, Empty

class Client(object):
    def __init__(self, handlerFunc = None):

        self._server = None
        self._port = None;
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._readfds = [self._client]

    def get_socket(self):
        return self._client

    def connect(self, server, port):
        self._server = server
        self._port = port
        self._client.connect((self._server, self._port))
        self._readfds = [self._client]
        pass

    def send(self, msg):
        self._client.send(msg)

    def recv(self, numbytes):
        return self._client.recv(numbytes)

    def client_thread(self):

        while True:
            readable, writable, errored = select.select(self._readfds, self._writefds,  [])

    def close(self):
        self._client.close()


class Server(object):
    def __init__(self, port, host=socket.gethostname(), maxclients=5, validate_func=None, timeout=None, verbose=False, useprocess=False, enablesend=True):
        """
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
            self._serverthread = multiprocessing.Process(target = self.server_thread)
        else:
            self._serverthread = Thread(target = self.server_thread)
            self._serverthread.daemon=True

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
        self._enablesend = ena

    def send_to_all_clients(self, data):
        if self._enablesend:
            #print('Port %d: Number of clients = %d, sendinprogress=%d'%(self._port, len(self._clients), int(self._sendinprogress)))
            for c in self._clients: 
                if self._sendinprogress is False:
                #if True:
                    #print('send_to_all_clients: qsize=%d'%(self._message_queues[c].qsize()))
                    self._message_queues[c].put_nowait(data)
                    if c not in self._writefds:
                        self._writefds.append(c)
                        #print('Port %d: Add client to writefds'%(self._port))
                else:
                    print('Port %d: SEND is BUSY'%(self._port))
                #if c not in self._writefds:
                #    self._writefds.append(c)
                #    print('Add client to writefds')
        else:
            print('** NOTE Gui server channel is disabled., port=%d'%(self._port))

    def has_clients(self):
        return True if len(self._clients) > 0 else False

    def server_thread(self):
        if self._verbose: print('Starting server thread: host=%s, port=%d'%(self._host, self._port))
        self._server.listen(self._maxclients)
        if self._exit:
            return
        self._readfds.append(self._server)
        #self._writefds.append(self._server)
        while True:
            try:
                ### Select: Detect activity in the server and client sockets
                readable, writable, errored = select.select(self._readfds, self._writefds, [], self._timeout)
                if not (readable or writable or errored):
                    ### Timeout
                    if self._exit:
                        if self._verbose:
                            print("Port %d: Exiting server: server=%s, port=%s"%(self._port, self._host, self._port))
                        for c in self._clients: 
                            self._readfds.remove(c)
                            if c in self._writefds:
                                self._writefds.remove(c)
                                print("Port %d: Removed client from writefs"%(self._port))
                            #self._clients.remove(c)
                            print("Port %d: Removed client from list"%(self._port))
                            c.close()
                            self._message_queues[c].put(None)
                            #del self._message_queues[c]
                        break
                    
                    #if self._verbose: print('Timeout...')
                    continue
                for s in readable:
                    ###################################
                    ####### Accept new connections
                    ###################################
                    if s is self._server: 
                        clientsock, addr = self._server.accept()
                        #clientsock.setblocking(0)
                        self._readfds.append(clientsock) # Add client socket into readfds list
                        self._clients.append(clientsock) # Add client socket into list of clients
                        ### Create a queue for each client
                        self._message_queues[clientsock] = Queue()
                        if self._verbose: print("Port %d: Received new client connection"%(self._port))

                ######################################
                ### Check if clients sent anything
                ######################################
                for c in self._clients: 
                    for s in readable:
                        if s is c:  ### Is the socket that has activity one of the clients???
                            data = c.recv(1024)
                            ### Client socket CLOSED
                            if not data: 
                                self._readfds.remove(c)
                                if c in self._writefds:
                                    self._writefds.remove(c)
                                    print("Port %d: Removed client from writefs"%(self._port))
                                self._clients.remove(c)
                                print("Port %d: Removed client from list"%(self._port))
                                c.close()
                                del self._message_queues[c]
                                print('Port %d: Closed client socket'%(self._port))
                            else:
                                #print('Received from client: %s'%(data))
                                #self._message_queues[c].put(data)
                                #if c not in self._writefds:
                                #    self._writefds.append(c)
                                #    print('Add client to writefds')
                                pass

                            continue
                    count = 0
                    for s in writable: ### If sockets available tor writting
                        #print('*******************************************************Writable....')
                        if s is c:  ### Is the socket that has activity one of the clients???
                            try:
                                next_msg = self._message_queues[c].get_nowait()
                                if next_msg is None:
                                    print('next_msg is None')
                                    continue
                            except Empty:
                                #print('Queue is EMPTY')
                                self._writefds.remove(c)
                                pass
                            else:
                                self._sendinprogress = True
                                msglen = len(next_msg)
                                #print('Port %d: sending data to client: %d bytes'%(self._port, msglen))
                                totallen = 0
                                start_time = time.time()
                                while totallen < msglen:
                                    ret = c.send(next_msg[totallen:])
                                    totallen += ret

                                #print('Port %d Sendall time: %d bytes; %f sec'%(self._port, totallen, time.time()-start_time), time.time(), datetime.datetime.now())
                                #self._writefds.remove(c)
                                self._sendinprogress = False

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print("Exception received: %s"%(repr(e)), exc_type, exc_tb.tb_lineno)
                self._sendinprogress =False 
                #self._server.close()
                #if self._q:
                #    self._q.put(None)
                #raise(e)
        print('Server Threaded Exit.')
        self._server.close()
                        
    def start(self):
        self._serverthread.start()

    def exit(self):
        print('Closing server')
        self._exit = True
        self._server.close()

if __name__ == "__main__":
    a = Server(8888, socket.gethostname(), verbose=True)

    a.start()
