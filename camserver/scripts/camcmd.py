import time
import socket
import struct

port = 2001
server = 'localhost' #socket.gethostname()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((server, port))

### Setup command
#cmd_str = "DISABLE_RECORDING"
#cmd_str = "ENABLE_RECORDING"
cmd_str = "GAIN=16"
cmd = cmd_str.encode().ljust(128, b'\0')
#client.sendall(cmd_msg)
client.sendall(cmd)
resp = client.recv(256)
print(resp)

