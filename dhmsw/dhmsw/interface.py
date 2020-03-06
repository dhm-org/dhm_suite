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
#  file:	interface.py
#  author:	S. Felipe Fregoso
#  description:	Contains classes of objects used as messages between components
###############################################################################
"""
import struct
import functools
import numpy as np

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
SRCID_IMAGE_ALL = 7
SRCID_TELEMETRY_BASENUM = 100
SRCID_TELEMETRY_HEARTBEAT = SRCID_TELEMETRY_BASENUM + 1
SRCID_TELEMETRY_RECONSTRUCTION = SRCID_TELEMETRY_BASENUM + 2
SRCID_TELEMETRY_HOLOGRAM = SRCID_TELEMETRY_BASENUM + 3
SRCID_TELEMETRY_FRAMESOURCE = SRCID_TELEMETRY_BASENUM + 4
SRCID_TELEMETRY_DATALOGGER = SRCID_TELEMETRY_BASENUM + 5
SRCID_TELEMETRY_GUISERVER = SRCID_TELEMETRY_BASENUM + 6
SRCID_TELEMETRY_SESSION = SRCID_TELEMETRY_BASENUM + 7
SRCID_TELEMETRY_FOURIERMASK = SRCID_TELEMETRY_BASENUM + 8
SRCID_TELEMETRY_ALL = SRCID_TELEMETRY_BASENUM + 9

class InitDonePkt():
    """
    Class of the "init_done" message.

    The messages is sent by the components to notify the controller
    that they are done initializing and ready to run
    """
    def __init__(self, name, errorcode):
        """
        Constructor
        """
        self._name = name
        self._errorcode = errorcode

    def get_errorcode(self):
        """
        Return the error code
        """
        return self._errorcode

    def get_name(self):
        """
        Return name of components
        """
        return self._name

class MessagePkt():
    """
    Class used to contain serialized data
    of images such as raw images, reconstructed images
    """
    def __init__(self, msg_id, src_id):
        """
        Constructor
        """
        self.databin = b''

        ### Packet Header
        self.msg_hdr = (msg_id, src_id)
        self.msg_hdr_struct = struct.Struct('III')

        self.ndim_struct = struct.Struct('H')

        self.pkt = None

    def header_size(self):
        """
        Calculates the size of the header in bytes
        """
        return struct.calcsize(self.msg_hdr_struct.format)

    def ndim_size(self):
        """
        Calculates and returns the number of dimensitions in message
        """
        return struct.calcsize(self.ndim_struct.format)

    def unpack_data(self, data, offset=0):
        """
        Unpacks the messages and returns message metadata and
        the content
        """
        headersize = self.header_size()
        ndimsize = self.ndim_size()

        meta = self.msg_hdr_struct.unpack(data[offset:offset+self.header_size()])
        _, srcid, _ = meta

        ndim = self.ndim_struct.unpack(data[headersize:headersize + ndimsize])[0]

        print("meta (msgtype, srcid, totbyte): ", meta)
        print(ndim)

        dimstruct = struct.Struct('H'*int(ndim))
        dimsize = struct.calcsize(dimstruct.format)
        dimensions = dimstruct.unpack(data[headersize + ndimsize:headersize + ndimsize + dimsize])

        offset = headersize + ndimsize + dimsize

        if srcid == SRCID_IMAGE_RAW:
            dtype = np.uint8
        else:
            dtype = np.float32

        offset_by_header = (functools.reduce(lambda x, y: x * y,\
                            dimensions) * np.dtype(dtype).itemsize)

        outdata = np.fromstring(data[offset:offset+offset_by_header], dtype=dtype)
        outdata = outdata.reshape(dimensions)

        return (meta, outdata)

    def serialize(self, data, append=False):
        """
        Serializes into a binary string the data and returns the binaryh string
        """
        binarystr = b''

        if isinstance(data, np.ndarray):
            binarystr += self.ndim_struct.pack(data.ndim) +\
            b''.join([struct.pack('H', c) for c in data.shape])

            binarystr += data.tobytes()

        elif isinstance(data, bytes):
            binarystr += data

        else:
            print('MessagePkt - serialize(): Unknown type', type(data))

        if append:
            self.databin += binarystr

        return binarystr

    def append(self, data):
        """
        Serialize data and append to binary string
        """
        return self.serialize(data, append=True)

    def reset_data(self):
        """
        Reset the internal binary string to empty string
        """
        self.databin = b''

    def complete_packet(self):
        """
        Complete the message packet by prepending the header
        as a binary string to the binary string.

        Returns a binary array
        """
        ### Construct header
        self.pkt = self.msg_hdr_struct.pack(*self.msg_hdr, len(self.databin))
        ### Append data
        self.pkt += self.databin

    def to_bytes(self):
        """
        Converts the packet string to binary array
        """
        return bytearray(self.pkt)

### Used for packets that from the DHM_Streaming software
class CamServerFramePkt():
    """
    Classed used for packets tha come from the camserver software
    """
    def __init__(self):
        """
        Constructor

        # *** See "include/CamFrame.h" of the camserver code
        # header[0] = unsigned long long int m_width
        # header[1] = unsigned long long int m_height
        # header[2] = unsigned long long int m_imgsize
        # header[3] = unsigned long long int m_databuffersize
        # header[4] = unsigned long long int m_timestamp
        # header[5] = unsigned long long int m_frame_id
        # header[6] = unsigned long long int m_logging;
        # header[7] = double                 m_gain;
        # header[8] = double                 m_gain_min;
        # header[9] = double                 m_gain_max;
        # header[10]= double                 m_exposure;
        # header[11]= double                 m_exposure_min;
        # header[12]= double                 m_exposure_max;
        # header[13]= double                 m_rate;
        # header[14]= double                 m_rate_measured;
        """
        self.pkt_hdr_struct = struct.Struct('QQQQQQQdddddddd')
        self._header = None
        self._header_size = None
        self._data = b''

    def header_packet_size(self):
        """
        Calculate and return the header size in bytes
        """
        #if self._header_size is None:
        self._header_size = struct.calcsize(self.pkt_hdr_struct.format)
        return self._header_size

    def unpack_header(self, data):
        """
        Extract the header from the binary data
        """
        self._header = self.pkt_hdr_struct.unpack(data[0:self.header_packet_size()])
        return self._header

    def set_data(self, data):
        """
        Set the data
        """
        self._data = data

    def header(self):
        """
        Return the header
        """
        self.unpack_header(self._data)
        return self._header

    def get_image(self):
        """
        Return the image data for the binary string
        """
        offset = self.header_packet_size()
        header = self.header()

        width = header[0]
        height = header[1]
        imgsize = header[2]
        data = np.fromstring(self._data[offset:offset+imgsize], dtype=np.uint8)
        data = np.reshape(data, (width, height))

        return data

class Command():
    """
    Class used to contain commands as they are sent to the components
    """
    def __init__(self, cmdobj=''):
        """
        Constructor
        """
        self._cmdobj = cmdobj

    def set_cmd(self, cmdobj):
        """
        Set the command object
        """
        self._cmdobj = cmdobj

    def get_cmd(self):
        """
        Return the command object
        """
        return self._cmdobj

class Image():
    """
    Class to contain an image as its sent to components
    """
    def __init__(self, meta=None, img=None):
        """
        Constructor
        """
        self._meta = meta
        self._img = img

    def set_img(self, meta, img):
        """
        Set the image and metadata
        """
        self._meta = meta
        self._img = img

    def get_img(self):
        """
        Return the image with its metadata
        """
        return (self._meta, self._img)

class ReconstructorProduct():
    """
    Class used to contain the reconstruction products as sent to the components
    """
    def __init__(self, image, hologram, ft_hologram, reconstwave, reconst_meta, holo_meta):
        """
        Constructor
        """
        # pylint: disable=too-many-arguments
        self.image = image
        self.hologram = hologram
        self.ft_hologram = ft_hologram
        self.reconstwave = reconstwave
        self.reconst_meta = reconst_meta
        self.holo_meta = holo_meta

    def get_reconst_product(self):
        """
        Get the reconstruction products which include the raw image and hologram object
        """
        return (self.image, self.hologram, self.reconstwave)

    def get_image(self):
        """
        Get image
        """
        return self.image

    def get_hologram(self):
        """
        Get hologram
        """
        return self.hologram

    def get_ft_hologram(self):
        """
        Get FT hologram
        """
        return self.ft_hologram

    def get_reconstwave(self):
        """
        Get Reconstruction Wave
        """
        return self.reconstwave


class GuiPacket():
    """
    Classed used to contain data to be sent to the GUI server component
    """
    def __init__(self, servername, data):
        """
        Constructor
        """
        self.servername = servername
        self.data = data

    def get_servername(self):
        """
        Return server name
        """
        return self.servername

    def get_data(self):
        """
        Return data
        """
        return self.data


class MetadataPacket():
    """
    Class to contain metadata as used to pass to components
    """
    def __init__(self, meta):
        """
        Constructor
        """
        self.meta = meta

    def get_meta(self):
        """
        Return meta
        """
        return self.meta

    def set_meta(self, meta):
        """
        Set meta
        """
        self.meta = meta
