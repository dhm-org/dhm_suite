import time
import socket
import struct

camFrame_struct = struct.Struct('QQQQQQ4194304B')
header_struct = struct.Struct('QQQQQQ')

framesize = struct.calcsize(camFrame_struct.format)

port = 2000
server = 'localhost' #socket.gethostname()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((server, port))

client.sendall(b"Hello World!!!")

data = ''
totalsize = 0
while True:
    packet = client.recv(framesize)
    if len(packet) <= 0: break;
    totalsize += len(packet)
    data += packet
    if totalsize >= framesize:
        frame = data[:framesize]
        data = data[framesize:]
        totalsize = 0;#len(data)
        #w, h, size,ts, fid = header_struct.unpack(frame[0:8+8+4+4+4+4]) #extra 4 for padding
        w, h, size,packetsize, ts, fid = header_struct.unpack(frame[0:8+8+8+8+8+8]) 
        print(time.time(), ts, fid, w, h, size, packetsize)

time.sleep(3)
client.close()
