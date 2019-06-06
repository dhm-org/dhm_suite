import time
import socket
import numpy as np

server = '127.0.0.1'
port = 9994

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server, port))

totalbytes = 5038872

i = 0
bytes_read = 0
print(time.time())
while (True):

    packet = sock.recv(totalbytes)
    bytes_read += len(packet)
    if bytes_read >= totalbytes:
        i+=1
        bytes_read -= totalbytes 
        print(time.time())
        print(bytes_read)

sock.close()
