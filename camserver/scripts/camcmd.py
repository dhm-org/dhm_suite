import sys
import time
import socket
import struct

class CamCmd():
    def __init__(self, server='localhost', port=2001):
        self._port = port
        self._server = server
        self._client = None

        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client.connect((server, port))

    def send(self, cmd_str):
        cmd = cmd_str.upper().encode().ljust(128, b'\0')
        self._client.sendall(cmd)
        resp = self._client.recv(256)
        print(resp)

        pass

def usage():
     print("Command List:")
     print("\tdisable_recording")
     print("\tenable_recording")
     print("\texit")
     print("\tsnap")
     print("\tgain <float>")

### Setup command
#cmd_str = "DISABLE_RECORDING"
cmd_str = "ENABLE_RECORDING"
#cmd_str = "STOP_IMAGING"
#cmd_str = "EXIT"
#cmd_str = "SNAP"
#cmd_str = "GAIN=26"

if __name__ == "__main__":
    print(usage())
    a = CamCmd()
    a.send("disable_recording")
