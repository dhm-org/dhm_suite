import socket
import select
import threading
from . import interface

class DHM_Command_Client(object):
    """ DHM Command Client
        Connect to the server, send the command string, then wait for a reply
        Raises exception if error connecting or timeout receiving command
    """
    def __init__(self, server='localhost', port=10000):
        self.server = server
        self.port = port
        self.sock = None

    def send(self, cmdstr):
        try:
            ### Create socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(2)
    
            ### Connect to server
            self.sock.connect((self.server, self.port))
            
            ### Send command string
            self.sock.send(cmdstr.encode())
    
            ### Wait for return acknowledment
            reply = self.sock.recv(1024)
            print(reply.decode()) 
            ### Close socket
            self.sock.close()
            self.sock = None

            ### Display return string
            return reply

        except socket.error as e:
            print('%s'%(repr(e)))
            if self.sock:
                self.sock.close()
                self.sock = None
            raise(e)

class DHM_Command_Server(threading.Thread):

    def __init__(self, hostname='localhost', port=10000, q=None, validate_func=None, blocking=False):
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
        #self._serverthread = Thread(target = self.server_thread)
        threading.Thread.__init__(self)
        self.daemon = True
        self._timeout = 1
        self._readfds = [self._server]
        self._validate_func = validate_func

    def run (self):
        self._server.listen(self._maxclients)
        while True:
            try:
                readable, writable, errored = select.select(self._readfds, [], [])
                if not (readable or writable or errored):
                    ### Timeout
                    continue
                for s in readable:
                    if s is self._server: # Accept new connections
                        clientsock, addr = self._server.accept()
                        if not self._blocking:        
                            clientsock.setblocking(0)
                        self._readfds.append(clientsock)
                        self._clients.append(clientsock)

                for c in self._clients: # Check if clients sent anything
                    for s in readable:
                        if s is c:
                            cmd_line = c.recv(1024)
                            print("Received: [%s]"%(cmd_line.decode()))
                            if not cmd_line: #Socket closed
                                self._readfds.remove(c)
                                self._clients.remove(c)
                                c.close()
                                print('Closed client socket')
                            else:
                                if self._q:
                                    if self._validate_func:
                                        (cmd, statusstr) = self._validate_func(cmd_line.decode())
                                        if cmd:
                                            replystr = "ACK: %s"%(statusstr)
                                            self._q.put_nowait(interface.Command(cmdobj=cmd))
                                            c.send(replystr.encode())
                                        else:
                                            replystr = "ERR: %s"%(statusstr)
                                            c.send(replystr.encode())
                                    else:
                                        self._q.put_nowait(cmd_line.decode())
                                        c.send("ACK".encode())
                            continue
            except Exception as e:
                self._server.close()
                #if self._q:
                #    self._q.put(None)
                raise(e)
                        
    #def start(self):
    #    self._serverthread.start()

    def exit(self):
        self._server.close()

