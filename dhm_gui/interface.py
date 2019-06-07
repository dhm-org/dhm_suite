import numpy as np
import struct
import functools

CMD_TYPE = 1 #1 << 12
TELEMETRY_TYPE = 2 #2 << 12
IMAGE_TYPE = 3 #3 << 12

SRCID_IMAGE_RAW = 0
SRCID_IMAGE_FOURIER = 1
SRCID_IMAGE_AMPLITUDE = 2
SRCID_IMAGE_PHASE = 3
SRCID_IMAGE_AMPLITUDE_AND_PHASE = 4
SRCID_IMAGE_INTENSITY = 5
SRCID_IMAGE_INTENSITY_AND_PHASE = 6
SRCID_TELEMETRY_BASENUM = 100
SRCID_TELEMETRY_HEARTBEAT= SRCID_TELEMETRY_BASENUM + 1
SRCID_TELEMETRY_RECONSTRUCTION =  SRCID_TELEMETRY_BASENUM + 2
SRCID_TELEMETRY_HOLOGRAM = SRCID_TELEMETRY_BASENUM + 3
SRCID_TELEMETRY_FRAMESOURCE = SRCID_TELEMETRY_BASENUM + 4
SRCID_TELEMETRY_DATALOGGER = SRCID_TELEMETRY_BASENUM + 5
SRCID_TELEMETRY_GUISERVER = SRCID_TELEMETRY_BASENUM + 6
SRCID_TELEMETRY_SESSION = SRCID_TELEMETRY_BASENUM + 7
SRCID_TELEMETRY_ALL = SRCID_TELEMETRY_BASENUM + 8

class MessagePkt(object):
    def __init__(self, msg_id, src_id):
        self.databin = b''

        ### Packet Header
        self.msg_hdr = (msg_id, src_id)
        self.msg_hdr_struct = struct.Struct('III')
 
        self.ndim_struct = struct.Struct('H')

    def header_size(self):
        return struct.calcsize(self.msg_hdr_struct.format)

    def ndim_size(self):
        return struct.calcsize(self.ndim_struct.format)

    def unpack_data(self, data, offset=0):
        headersize = self.header_size()
        ndimsize = self.ndim_size()

        meta = self.msg_hdr_struct.unpack(data[offset:offset+self.header_size()])
        msgtype, srcid, totbytes = meta
        ndim = self.ndim_struct.unpack(data[headersize:headersize + ndimsize])[0]

        print("msgtype=%d, srcid=%d, totbytes=%d"%(msgtype, srcid, totbytes))
        print(ndim)
        
        dimstruct = struct.Struct('H'*int(ndim))
        dimsize = struct.calcsize(dimstruct.format)
        dimensions = dimstruct.unpack(data[headersize + ndimsize:headersize + ndimsize + dimsize])

        offset = headersize + ndimsize + dimsize

        if srcid == SRCID_IMAGE_FOURIER:
            dtype = np.compllex64
        elif srcid == SRCID_IMAGE_RAW:
            dtype = np.uint8
        else:
            dtype = np.float32

        outdata = np.fromstring(data[offset:offset+(functools.reduce(lambda x,y: x*y, dimensions)*np.dtype(dtype).itemsize)], dtype=dtype).reshape(dimensions)

        return (meta, outdata)

    def serialize(self,data, append=False):
        binarystr = b''
        if type(data) is np.ndarray:
            binarystr += self.ndim_struct.pack(data.ndim) + b''.join([struct.pack('H',c) for c in data.shape])
            binarystr += data.tobytes()
        elif type(data) is bytes:
            binarystr += data
        else:
           print('Unkonwn type', type(data))

        if append: self.databin += binarystr
 
        return binarystr

    def append(self, data):
        return self.serialize(data, append=True)

    def reset_data(self):
        self.databin = b''

    def complete_packet(self):
        ### Construct header
        self.pkt = self.msg_hdr_struct.pack(*self.msg_hdr, len(self.databin))
        ### Append data
        self.pkt += self.databin
    def to_bytes(self):
        return bytearray(self.pkt)
        
### Used for packets that from the DHM_Streaming software
class MicroscopePkt(object):
    def __init__(self):
        self.pkt_hdr_struct = struct.Struct('HHHBIIIHH')
        self._header = None
        self._header_size = None
        self.data = b''

    @property
    def header_packet_size(self):
        if self._header_size is None:
            self._header_size = struct.calcsize(self.pkt_hdr_struct.format)
        return self._header_size

    def unpack_header(self, data):
        self._header = self.pkt_hdr_struct.unpack(data[0:self.header_packet_size])
        return self._header

    def set_data(self, data):
        self._data = data

    @property
    def header(self):
        if self._header is None:
            self.unpack_header(self._data)
        return self._header

    def get_image(self):
        offset = self.header_packet_size
        header = self.header

        data = np.fromstring(self._data[offset:offset+header[5]], dtype=np.uint8)
        data = np.reshape(data, (header[1],header[0]))
        return data

class Command(object):
    def __init__(self, cmdobj=''):
        self._cmdobj = cmdobj 

    def set_cmd(self, cmdobj):
        self._cmdobj = cmdobj

    def get_cmd(self):
        return self._cmdobj

class Image(object):
    def __init__(self, meta=None, img=None):
        self._meta = meta
        self._img = img
    def set_img(self, meta, img):
        self._meta = meta
        self._img = img

    def get_img(self):
        return (self._meta, self._img)

class ReconstructorProduct(object):
    def __init__(self, image, hologram, reconstwave, reconst_meta, holo_meta):
        self.image = image
        self.hologram = hologram
        self.reconstwave = reconstwave
        self.reconst_meta = reconst_meta
        self.holo_meta = holo_meta

    def get_reconst_product(self):
        return (self.image, self.hologram, self.reconstwave)

class GuiPacket(object):
    def __init__(self, servername, data):
        self.servername = servername
        self.data = data

class MetadataPacket(object):
    def __init__(self, meta):
        self.meta = meta

if __name__ == '__main__':
    pass
    #print(a.serialize()[0:20])
