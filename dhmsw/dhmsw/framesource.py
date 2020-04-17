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
#  file:	framesource.py
#  author:	S. Felipe Fregoso
#  description:	Module that gets image frames either from disk, camera server,
#               or from some remote location (TBD).
#
#               A seperate thread is used to get images from the camera server
#               or from disk.
###############################################################################
"""
import sys
import socket
import copy
import select
import glob
import threading
import time
import queue
from skimage.io import imread
import numpy as np

from . import sequence
from . import interface as Iface
from . import metadata_classes as MetaC
from .heartbeat import Heartbeat as HBeat
from .component_abc import ComponentABC

def verboseprint(*args, **kwargs):
    """
        Print statement if verbose is enabled
    """
    print(*args, **kwargs)

def _get_img_obj(img):
    """
    Return a 2D array which is the image.
    Sometimes readin from a file produces 3D array
    """
    imgobj = None

    if img.shape == 3:
        imgobj = Iface.Image((), img[:, :, 0])
    else:
        imgobj = Iface.Image((), img)

    return imgobj

def client_connect(host, port):
    """
    Wrapper function to connect to client
    """

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        return client
    except socket.error as err:
        print("Unable to connect to the client: [%s]"%(repr(err)))
        raise err

def process_cmd(opcode, arg, tempmeta):
    """
    Process commands
    """
    validcommand = True
    wanttorun = False

    if opcode == 'mode':
        if arg == 'file':
            tempmeta.mode = arg
        elif arg == 'camera':
            tempmeta.mode = arg
        elif arg == 'sequence':
            tempmeta.mode = arg
        else:
            print('Unknown mode [%s]'%(arg))
            validcommand = False
    elif opcode == 'exec':
        if arg == 'run':
            wanttorun = True
        elif arg == 'idle':
            wanttorun = False
        else:
            validcommand = False
            print('Unknown exec mode [%s]'%(arg))
            wanttorun = None
    elif opcode == 'filepath':
        tempmeta.file['datadir'] = arg
    else:
        print('Framesource:  Unknown parameter [%s].'%(opcode))
        validcommand = False

    return (validcommand, wanttorun)

class Framesource(ComponentABC):
    """
        Module to get frames from cameras or from file
    """
    def __init__(self, identifier, inq, pub, _events, configfile=None, verbose=False):
        """
        Overload __init__
        """
        # pylint: disable=too-many-arguments
        ComponentABC.__init__(self,
                              identifier,
                              inq,
                              pub,
                              _events,
                              configfile=configfile,
                              verbose=verbose)

        self._reconst_meta = self._allmeta.metadata['RECONSTRUCTION']
        self._meta.state = MetaC.FramesourceMetadata.FRAMESOURCE_STATE_IDLE

        self._filegenerator = {}

        self._camclihandler = {}
        ### Declare camera server frame packet object
        self._ms_pkt = Iface.CamServerFramePkt()


    def is_filegenerator_alive(self):
        """
        Indicates if file generator thread is running
        """
        return self._filegenerator['thread'].is_alive()

    def start_filegenerator(self, filepath):
        """
        Starts the thread to read from a file and publish images and sets state to RUNNING.

        Checks to see if 'filegenerator' thread is already running, if so then

        Parameters
        --------------
        filepath : str

        Returns
        --------------
        bool
            TRUE if file generator thread has been spawned.  FALSE if otherwise due to
            thread is already running or error encountered

        """

        if self.is_filegenerator_alive():
            print('Filegenerator thread is already running')
            return False

        ### Stop any thread that is publishing images.
        self.stop_imagegenerator()

        ### Get list of files
        flist = []
        #if type(filepath) is list:
        if isinstance(filepath, list):
            for fname in filepath:
                lst = glob.glob(fname)
                for _ in lst:
                    flist.append(_)
        else:
            flist = glob.glob(filepath)

        ### Spawn thread if filepath produced a list of files.
        ret = False
        if flist:
            self._filegenerator['thread'] = threading.Thread(
                target=self._file_thread,
                args=(flist,
                      self._filegenerator['queue'],
                      self._events['reconst']['done'],
                      )
                )
            self._filegenerator['thread'].daemon = True
            self._filegenerator['thread'].start()
            self._meta.state = MetaC.FramesourceMetadata.FRAMESOURCE_STATE_RUNNING
            ret = True
        else:
            print('No files returned from given filepath=[%s]'%(filepath))

        return ret


    def _stop_filegenerator(self):
        if self._filegenerator['thread'].is_alive():
            self._filegenerator['queue'].put_nowait(None)
            self._filegenerator['thread'].join()
            print('Stopped filegenerator thread')

    def _stop_cameraclient(self):
        if self._camclihandler['thread'].is_alive():
            ## Need to stop thread first
            self._camclihandler['queue'].put_nowait(None)
            self._camclihandler['thread'].join()
            print('Stopped clienthandler thread')

    def stop_imagegenerator(self):
        """
        Stop currently executing threads
        (either image generator from files, or
        camera images) that is publishing images and
        sets state to IDLE

        Parameters
        --------------
        None

        Returns
        --------------
        None

        """

        self._stop_filegenerator()
        self._stop_cameraclient()
        self._meta.state = MetaC.FramesourceMetadata.FRAMESOURCE_STATE_IDLE


    def _file_thread(self, flist, inq, reconst_done_event):
        """
        Thread that reads images from a file and publishes it.

        This thread is spawned by function 'start_filegenerator'.  If the
        reconstruction mode is RECONST_NONE then this thread will publish
        images at a rate of 6Hz in the order they are in 'flist'.  If the
        reconstruction mode is anything other than RECONST_NONE, then it will
        publish the image and wait for signal to be raised by the Reconstructor
        module to indicate that it is done reconstructing.  Once the signal is
        received the next image is published.

        This thread will terminate if all files in 'flist' have been published
        or if a 'None' messages is sent in 'inq'

        Parameters
        ---------------
        flist : list
            List of file paths to image files.
        inq : queue.Queue
            Input message queue.  Primarily used to get a 'None' message to
            terminate the thread.
        reconst_done_event :
            TBD

        Returns
        ---------------
        None
        """

        verbose = True
        numfiles = len(flist)
        count = 0
        ### Send first file
        img = np.asarray(imread(flist[0]))

        imgobj = _get_img_obj(img)

        self._meta.file['currentfile'] = flist[0]

        self.publish_image(imgobj)
        verboseprint('%f: Sent count=%d, total=%d, fname=%s'%(time.time(),
                                                              count,
                                                              numfiles,
                                                              flist[count])
                    )
        while True:
            try:
                ret = inq.get_nowait() #Mainly used to get a 'None' to end the execution
                if ret is None:
                    break
            except queue.Empty:
                pass

            if self._reconst_meta.processing_mode == MetaC.ReconstructionMetadata.RECONST_NONE:
                count += 1
                if count >= numfiles:
                    break
                self._meta.file['currentfile'] = flist[count]
                img = np.asarray(imread(flist[count]))

                imgobj = _get_img_obj(img)

                #reconst_done_event.clear()
                self.publish_image(imgobj)
                time.sleep(.166) #6Hz
                if verbose:
                    print('%f: Sent count=%d, total=%d, fname=%s'%(time.time(),
                                                                   count,
                                                                   numfiles,
                                                                   flist[count])
                         )
                print('Done event timed out')
            else:
                reconst_done_event.wait(3)
                if verbose:
                    print('%f: Done event received, count=%d, total=%d, '
                          'fname=%s'%(time.time(),
                                      count,
                                      numfiles,
                                      flist[count]))
                count += 1
                if count >= numfiles:
                    break
                self._meta.file['currentfile'] = flist[count]
                img = np.asarray(imread(flist[count]))
                if img.shape == 3:
                    imgobj = Iface.Image((), img[:, :, 0])
                else:
                    imgobj = Iface.Image((), img)

                reconst_done_event.clear()
                self.publish_image(imgobj)
                if verbose:
                    print('%f: Sent count=%d, total=%d, '
                          'fname=%s'%(time.time(),
                                      count,
                                      numfiles,
                                      flist[count]))

        print('File Generation thread ended')
        inq.queue.clear()
        self._meta.state = MetaC.FramesourceMetadata.FRAMESOURCE_STATE_IDLE
        self.publish_status()

    def start_camera_client(self):
        """
        Start the client to the camera server.

        Parameters
        -------------
        None

        Returns
        -------------
        None

        """

        if self._camclihandler['thread'].is_alive():
            print('Client thread already running')
            return True

        ### Check if clienhandler thread is running
        #if self._filegenerator['thread'].is_alive():
        #    ## Need to stop thread first
        #    self._filegenerator['queue'].put_nowait(None)
        #    self._filegenerator['thread'].join()
        #    self._meta.state = MetaC.FramesourceMetadata.FRAMESOURCE_STATE_IDLE
        self.stop_imagegenerator()

        try:
            clientsock = client_connect(self._meta.camserver.host,
                                        self._meta.camserver.ports['frame'])
            self._camclihandler['thread'] = \
                threading.Thread(target=self._camcli_thread,
                                 args=(clientsock,
                                       self._camclihandler['queue'],
                                       self._inq)
                                )
            self._camclihandler['thread'].daemon = True
            self._camclihandler['thread'].start()

            self._meta.state = MetaC.FramesourceMetadata.FRAMESOURCE_STATE_RUNNING
            return True
        except socket.error as err:
            print('ERROR: Unable to connect to server. [%s]'%(repr(err)))
            self._meta.state = MetaC.FramesourceMetadata.FRAMESOURCE_STATE_IDLE
            return False

    def publish_status(self, status_msg=None):
        """
        Publish the status of the Framesource module.  Update the status if passed in.

        Parameters
        --------------
        status_msg : str
            If not None, then status message is updated before its sent.

        Returns
        --------------
        None

        """

        if status_msg:
            self._meta.status_msg = status_msg
        self._pub.publish('framesource_status', Iface.MetadataPacket(self._meta))

    def publish_image(self, img):
        """
        Publish a raw image.

        Parameters
        --------------
        img : Iface.Image
            Image that will be published to all subscribers of this data.

        Returns
        ---------------
        None

        """

        self._pub.publish('rawframe', img)

    def process_metadata(self, data):
        """
        Process metadata

        Updates the internal meta data variable based on the metadata type.

        Parameters
        --------------
        data : Iface.MetadataPacket

        Returns
        --------------
        None

        """

        if isinstance(data, Iface.MetadataPacket):
            meta = data.meta
        else:
            meta = data

        meta_type = type(meta)

        if meta_type is MetaC.ReconstructionMetadata:
            print('Framesource: Received "ReconstructionMetadata"')
            self._reconst_meta = meta
        elif meta_type is MetaC.ReconstructionDoneMetadata:
            pass

    def _start_sequence(self):
        try:
            flist = sequence.Sequence().get_sequence_filepaths(self._meta.file['datadir'])
            self.start_filegenerator(flist)
        except (ValueError, IOError) as err:
            self._meta.status_msg = 'ERROR with sequence: %s'%(repr(err))
            print(self._meta.status_msg)

    def _wanttorun(self, wanttorun):
        if wanttorun is not None:
            if not wanttorun:
                self.stop_imagegenerator()
            else:
                print('Mode = [%s]'%(self._meta.mode))
                if self._meta.mode == 'camera':
                    self.start_camera_client()
                elif self._meta.mode == 'file':
                    self.start_filegenerator(self._meta.file['datadir'])
                elif self._meta.mode == 'sequence':
                    self._start_sequence()
                else:
                    self._meta.status_msg = 'INVALID mode [%s] for framesource'%(self._meta.mode)
                    print(self._meta.status_msg)

    def _initialize_framereceivethreads(self):
        """
        Initialize the threads that will generate frames
        """
        self._filegenerator['thread'] = threading.Thread(target=None)
        self._filegenerator['queue'] = queue.Queue()
        self._camclihandler['thread'] = threading.Thread(target=None)
        self._camclihandler['queue'] = queue.Queue()

    def process_component_message(self, data):
        """
        Process the message from the component port
        """
        ### Process command
        if isinstance(data, Iface.Command):

            cmd = data.get_cmd()
            tempmeta = copy.copy(self._meta)
            validcommand = True
            wanttorun = None
            print('Framesource got command')
            print(cmd)

            for modid, var in cmd.items():
                if modid == 'framesource':
                    if not var: ### Empty parameter list, send reconst status
                        break
                    for opcode, arg in var.items():
                        validcommand, wanttorun = process_cmd(opcode, arg, tempmeta)
                        if not validcommand:
                            break
                else:
                    validcommand = False
                    print('Module ID [%s] is not valid for Framesource'%(modid))
                    break

                #if not validcommand:
                #    break

            if validcommand:
                self._meta = copy.copy(tempmeta)
                self._meta.status_msg = 'SUCCESS'
                self._wanttorun(wanttorun)
                self.publish_status()

        elif isinstance(data, Iface.MetadataPacket):
            self.process_metadata(data)

        ### Process image (from camera streamer)
        elif isinstance(data, type(b'')):
            self._ms_pkt.set_data(data)
            framedata = Iface.Image(self._ms_pkt.header(), self._ms_pkt.get_image())
            self.publish_image(framedata)
            print("%f: Got Frame!"%(time.time()))
        elif isinstance(data, Iface.Image):
            self.publish_image(data)
            print("Framesource: %f: Got Image Frame!"%(time.time()))
        else:
            print('Unkown type', type(data))


    def create_heartbeat(self):
        """
        Create the heartbeat object
        """
        self._hbeat = HBeat(self._pub, self._id.lower())

    def start_heartbeat(self):
        """
        Start the heartbeat
        """
        self._hbeat.start()

    def terminate_heartbeat(self):
        """
        End the execution of this components heartbeat
        """
        self._hbeat.terminate()

    def notify_controller_and_wait(self):
        """
        Notify the controller component that this component is ready
        and wait for controller component OK to start running
        """
        self._pub.publish('init_done', Iface.InitDonePkt('Framesource', 0))
        print('[%s] Consumer thread started'%(self._id))
        self._events['controller']['start'].wait()

    def run(self):
        """
        Component execution loop
        """

        try:

            self._initialize_framereceivethreads()

            self.create_heartbeat()

            self.notify_controller_and_wait()

            self.start_heartbeat()
            print('[%s] Consumer thread started'%(self._id))

            while True:

                data = self._inq.get()

                if data is None:
                    print('Exiting [%s]'%(self._id))
                    break

                ### Process Messages
                self.process_component_message(data)

            ## End of While
            self.end_component()

        except Exception as err:
            self.handle_component_exception(err)

        finally:
            self.stop_imagegenerator()

    def handle_component_exception(self, err):
        """
        Send Heartbeat error and raise the error
        """
        print('[%s] Exception caught: %s'%(self._id, repr(err)))
        exc_type, exc_obj, t_b = sys.exc_info()
        lineno = t_b.tb_lineno
        print('{} EXCEPTION IN (LINE {}): {}'.format(self._id, lineno, exc_obj))

        self._hbeat.set_update(err)
        if self._hbeat.isAlive():
            self._hbeat.join(timeout=5)
        raise err

    def end_component(self):
        """
        End execution of component
        """
        self.terminate_heartbeat()
        if self._hbeat.isAlive():
            self._hbeat.join(timeout=5)
        self.stop_imagegenerator()
        print('[%s]: End'%(self._id))

    def _camcli_thread(self, clientsock, inq, outq):
        """
        Camera client thread.  Gets frames from the camera server
        """
        readfds = [clientsock]
        exitthread = False
        verbose = False

        count = 0

        data = b''
        msg = b''
        lasttime = time.time()
        meta = None
        totalbytes = 0

        ms_pkt = Iface.CamServerFramePkt()

        print('Started client thread')
        while True:
            if exitthread:
                print("Framesource: Exiting _camcli thread")
                break

            infds, outfds, errfds = select.select(readfds, [], [], 1)

            if not (infds or outfds or errfds):
                ### TIMEOUT
                ### Check if any input data from queue
                try:
                    qdata = inq.get_nowait()
                    if qdata is None: ### Exit the thread
                        print('^^^^^^^^^^^ Closed Camera Thread ^^^^^^^^^')
                        clientsock.close()
                        exitthread = True
                        continue
                except queue.Empty:
                    pass

                continue

            try:
                # Graceful exit of thread
                qdata = inq.get_nowait()
                if qdata is None: ### Exit the thread
                    clientsock.close()
                    return
            except queue.Empty:
                pass

            for in_sock in infds:
                if in_sock is clientsock:
                    ### Get as much data as we can
                    packet = clientsock.recv(65535)

                    if not packet:
                        print("Framesource: Camera server disconnected. Closing socket.")
                        clientsock.close()
                        exitthread = True
                        break

                    data += packet
                    datalen = len(data)

                    ### If he haven't processed the header/meta, then lets.
                    if meta is None and datalen > ms_pkt.header_packet_size():
                        height, \
                        width, \
                        size, \
                        packetsize, \
                        tstamp, \
                        frameid, \
                        logging, \
                        gain, \
                        gain_min, \
                        gain_max, \
                        exposure, \
                        exposure_min, \
                        exposure_max, \
                        rate, \
                        rate_measured = ms_pkt.unpack_header(data)
                        meta = ( \
                                height,\
                                width, \
                                size, \
                                packetsize, \
                                tstamp, \
                                frameid, \
                                logging, \
                                gain, \
                                gain_min, \
                                gain_max, \
                                exposure, \
                                exposure_min, \
                                exposure_max, \
                                rate, \
                                rate_measured, \
                               )
                        totalbytes = packetsize + ms_pkt.header_packet_size()

                        if datalen >= totalbytes:  ### We have a complete packet stored.
                            msg = data[:totalbytes]
                            data = data[totalbytes:]
                            meta = None
                            totalbytes = 0
                            if verbose:
                                print('%.2f Hz'%(1/(time.time()-lasttime)))
                            lasttime = time.time()
                            count += 1
                            outq.put_nowait(msg)
                            if verbose:
                                print('%f: Full message received after getting'
                                      'meta: datalen=%d, datalen after=%d'%(time.time(), datalen, len(data)))
                    else:
                        if datalen < totalbytes:
                            continue

                        ### We have a complete message
                        msg = data[:totalbytes]
                        data = data[totalbytes:]
                        if verbose:
                            print('%f: Full message received: datalen=%d, '
                                  'datalen after=%d'%(time.time(),
                                                      datalen,
                                                      len(data)))
                        meta = None
                        totalbytes = 0
                        ### Send frame here
                        outq.put_nowait(msg)
                        if verbose:
                            print('%.2f Hz'%(1/(time.time()-lasttime)))
                        lasttime = time.time()
                        count += 1
        print('Framesource:  End of Camera Client Thread')
        inq.queue.clear()
        self._meta.state = MetaC.FramesourceMetadata.FRAMESOURCE_STATE_IDLE
        self.publish_status()
