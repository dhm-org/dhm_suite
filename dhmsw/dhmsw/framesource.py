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
import sys
import socket
import copy
import select
import glob
import multiprocessing
import threading
import time
import queue
from skimage.io import imread

from . import sequence
from . import interface
from . import metadata_classes
from .heartbeat import Heartbeat

class Framesource(multiprocessing.Process):
    def __init__(self, inq, pub, _events, configfile=None, verbose=False):
        """
        Constructor of the Framesource class

        Initializes state to IDLE and copies inputs into class member variables

        Parameters
        -------------
        inq : multiprocessing.queues.Queue
            Queue for input messages into the process.
        pub : dhmpubsub.PubSub
            Handle to the publish/subscribe object
        _events :
            Event to wait for signal indicating reconstruct of an image has completed
        verbose : boolean
            If TRUE print detail information to terminal, FALSE otherwise.

        Returns
        --------------
        None

        """

        multiprocessing.Process.__init__(self)

        self._verbose = verbose
        #### Create the consumer thread for this module
        self._inq = inq
        self._events = _events 
        self._pub = pub

        meta = metadata_classes.Metadata_Dictionary(configfile)
        self._meta = meta.metadata['FRAMESOURCE']
        self._reconst_meta = meta.metadata['RECONSTRUCTION']
        self._meta.state = metadata_classes.Framesource_Metadata.FRAMESOURCE_STATE_IDLE

        ## Heartbeat
        self._HB = None

        ### Threads
        self._filegenerator = {}

        self._camclienthandler = {}

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

        if self._filegenerator['thread'].is_alive():
            print('Filegenerator thread is already running')
            return False

        ### Stop any thread that is publishing images.
        self.stop_imagegenerator()

        ### Get list of files
        flist = []
        if type(filepath) is list:
            for f in filepath:
                lst = glob.glob(f)
                for _ in lst:
                    flist.append(_)
        else:
            flist = glob.glob(filepath)

        ### Spawn thread if filepath produced a list of files.
        if flist:
            self._filegenerator['thread']= threading.Thread(target=self._file_thread, args=(flist, self._filegenerator['queue'], self._events['reconst']['done']))
            self._filegenerator['thread'].daemon = True
            self._filegenerator['thread'].start()
            self._meta.state = metadata_classes.Framesource_Metadata.FRAMESOURCE_STATE_RUNNING
            return True
        else:
            print('No files returned from given filepath=[%s]'%(filepath))
        return False

    def stop_imagegenerator(self):
        """
        Stop currently executing thread that is publishing images and sets state to IDLE

        Parameters
        --------------
        None

        Returns
        --------------
        None

        """
        if self._filegenerator['thread'].is_alive():
            self._filegenerator['queue'].put_nowait(None)
            self._filegenerator['thread'].join()
            print('Stopped filegenerator thread')

        if self._camclienthandler['thread'].is_alive():
            ## Need to stop thread first
            self._camclienthandler['queue'].put_nowait(None)
            self._camclienthandler['thread'].join()
            print('Stopped clienthandler thread')

        self._meta.state = metadata_classes.Framesource_Metadata.FRAMESOURCE_STATE_IDLE

    def _file_thread(self, flist, inq, reconst_done_event):
        """
        Thread that reads images from a file and publishes it.

        This thread is spawned by function 'start_filegenerator'.  If the reconstruction mode is RECONST_NONE then
        this thread will publish images at a rate of 6Hz in the order they are in 'flist'.
        If the reconstruction mode is anything other than RECONST_NONE, then it will publish the image and 
        wait for signal to be raised by the Reconstructor module to indicate that it is done reconstructing.
        Once the signal is received the next image is published.

        This thread will terminate if all files in 'flist' have been published or if a 'None' messages is sent in 'inq'

        Parameters
        ---------------
        flist : list
            List of file paths to image files.
        inq : queue.Queue
            Input message queue.  Primarily used to get a 'None' message to terminate the thread.
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
        img = imread(flist[0])
        if img.shape == 3:
            a = interface.Image((), img[:,:,0])
        else:
            a = interface.Image((), img)
        self._meta.file['currentfile'] = flist[0]

        self.publish_image(a)
        if verbose: print('%f: Sent count=%d, total=%d, fname=%s'%(time.time(), count, numfiles, flist[count]))
        while True:
            try:
                ret = inq.get_nowait() #Mainly used to get a 'None' to end the execution
                if ret is None:
                    break
            except queue.Empty:
                pass

            if self._reconst_meta.processing_mode == metadata_classes.Reconstruction_Metadata.RECONST_NONE:
                count += 1
                if count >= numfiles:
                    break
                self._meta.file['currentfile'] = flist[count]
                img = imread(flist[count])
                if img.shape == 3:
                    a = interface.Image((), img[:,:,0])
                else:
                    a = interface.Image((), img)

                #reconst_done_event.clear()
                self.publish_image(a)
                time.sleep(.166) #6Hz
                if verbose: print('%f: Sent count=%d, total=%d, fname=%s'%(time.time(), count, numfiles, flist[count]))
                print('Done event timed out')
            else:
                if True:
                    reconst_done_event.wait(3)
                    if verbose: print('%f: Done event received, count=%d, total=%d, fname=%s'%(time.time(), count, numfiles, flist[count]))
                    count += 1
                    if count >= numfiles:
                        break
                    self._meta.file['currentfile'] = flist[count]
                    img = imread(flist[count])
                    if img.shape == 3:
                        a = interface.Image((), img[:,:,0])
                    else:
                        a = interface.Image((), img)
    
                    reconst_done_event.clear()
                    self.publish_image(a)
                    if verbose: print('%f: Sent count=%d, total=%d, fname=%s'%(time.time(), count, numfiles, flist[count]))

        print('File Generation thread ended')
        inq.queue.clear()
        self._meta.state = metadata_classes.Framesource_Metadata.FRAMESOURCE_STATE_IDLE
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

        if self._camclienthandler['thread'].is_alive():
            print('Client thread already running')
            return True 

        ### Check if clienhandler thread is running
        #if self._filegenerator['thread'].is_alive():
        #    ## Need to stop thread first
        #    self._filegenerator['queue'].put_nowait(None)
        #    self._filegenerator['thread'].join()
        #    self._meta.state = metadata_classes.Framesource_Metadata.FRAMESOURCE_STATE_IDLE
        self.stop_imagegenerator()

        try:
            clientsock = self._camclient_connect(self._meta.camserver.host, self._meta.camserver.ports['frame'])
            self._camclienthandler['thread'] = threading.Thread(target=self._camclient_thread, args=(clientsock, self._camclienthandler['queue'], self._inq, self._events['reconst']['done'])) 
            self._camclienthandler['thread'].daemon = True
            self._camclienthandler['thread'].start()

            self._meta.state = metadata_classes.Framesource_Metadata.FRAMESOURCE_STATE_RUNNING
            return True
        except socket.error as e:
            print('ERROR: Unable to connect to server. [%s]'%(repr(e)))
            self._meta.state = metadata_classes.Framesource_Metadata.FRAMESOURCE_STATE_IDLE
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
        self._pub.publish('framesource_status',interface.MetadataPacket(self._meta))

    def publish_image(self, img):
        """
        Publish a raw image.

        Parameters
        --------------
        img : interface.Image
            Image that will be published to all subscribers of this data.

        Returns
        ---------------
        None

        """

        self._pub.publish('rawframe',img)

    def process_metadata(self, data):
        """
        Process metadata

        Updates the internal meta data variable based on the metadata type.

        Parameters
        --------------
        data : interface.MetadataPacket

        Returns
        --------------
        None

        """

        if type(data) is interface.MetadataPacket:
            meta = data.meta
        else:
            meta = data

        meta_type = type(meta)

        if meta_type is metadata_classes.Reconstruction_Metadata:
            print('Framesource: Received "Reconstruction_Metadata"')
            self._reconst_meta = meta;
        elif meta_type is metadata_classes.Reconstruction_Done_Metadata:
            pass
        
        pass

    def run(self):

        try:
            self._filegenerator['thread'] = threading.Thread()
            self._filegenerator['queue'] = queue.Queue()
            self._camclienthandler['thread'] = threading.Thread()
            self._camclienthandler['queue'] = queue.Queue()

            ### Start Hearbeat
            self._HB = Heartbeat(self._pub, 'framesource')
    
            ### Declare camera server frame packet object
            msPkt = interface.CamServerFramePkt()
    
            ### Publish 'init_done' message indicating that Framesource has started to run.
            self._pub.publish('init_done', interface.InitDonePkt('Framesource', 0))

            ### Wait for the Controller module to signal start
            self._events['controller']['start'].wait()

            ### Start the hearbeat for the Framesource
            self._HB.start()

            print('Framesource Consumer thread started')
            while True:
                data = self._inq.get()
                if data is None:
                    print('Exiting Framesource')
                    break
    
                ### Process command
                if type(data) is interface.Command:
                    cmd = data.get_cmd()
                    tempmeta = copy.copy(self._meta)
                    validcommand = True
                    changemode = False
                    wanttorun = None
                    print('Framesource got command')
                    print(cmd)
                    for k, v in cmd.items():
                        if k == 'framesource':
                            if not v: ### Empty parameter list, send reconst status
                                break
                            for kk, vv in v.items():
                                if kk == 'mode':
                                    changemode = True
                                    if vv == 'file':
                                        tempmeta.mode = vv
                                        pass
                                    elif vv == 'camera':
                                        tempmeta.mode = vv
                                        pass
                                    elif vv == 'sequence':
                                        tempmeta.mode = vv
                                        pass
                                    else:
                                        print('Unknown mode [%s]'%(vv))
                                        validcommand = False
                                        changemode = False
                                elif kk == 'exec':
                                    if vv == 'run':
                                        wanttorun = True;
                                    elif vv == 'idle':
                                        wanttorun = False;
                                    else:
                                        validcommand = False
                                        print('Unknown exec mode [%s]'%(vv))
                                        wanttorun = None
                                elif kk == 'filepath':
                                    tempmeta.file['datadir'] = vv
                                else:
                                    print('Framesource:  Unknown parameter [%s].'%(kk))
                                    validcommand = False
    
                                if validcommand == False: break
                        else:
                            validcommand = False
                            print('Command [%s] is not valid'%(k))
                            break
    
                        if validcommand == False: break
    
                    if validcommand:
                        self._meta = copy.copy(tempmeta)
                        self._meta.status_msg = 'SUCCESS'
                        if wanttorun is not None:
                            if wanttorun == False:
                                self.stop_imagegenerator()
                            else:
                                print('Mode = [%s]'%(self._meta.mode))
                                if self._meta.mode == 'camera':
                                    self.start_camera_client()
                                elif self._meta.mode == 'file':
                                    self.start_filegenerator(self._meta.file['datadir'])
                                elif self._meta.mode == 'sequence':
                                    try:
                                        flist = sequence.Sequence().get_sequence_filepaths(self._meta.file['datadir'])
                                        self.start_filegenerator(flist)
                                    except (ValueError, IOError) as e:
                                        self._meta.status_msg = 'ERROR with sequence: %s'%(repr(e))
                                        print(self._meta.status_msg)
                                else:
                                    self._meta.status_msg = 'INVALID mode [%s] for framesource'%(self._meta.mode)
                                    print(self._meta.status_msg)
                        self.publish_status()
                elif isinstance(data, interface.MetadataPacket):
                    self.process_metadata(data)
    
                ### Process image (from camera streamer)
                elif type(data) is type(b''):
                    msPkt.set_data(data)
                    framedata = interface.Image(msPkt.header(), msPkt.get_image())
                    self.publish_image(framedata)
                    print("%f: Got Frame!"%(time.time()))
                elif type(data) is interface.Image:
                    self.publish_image(data)
                    print("Framesource: %f: Got Image Frame!"%(time.time()))
                else:
                    print('Unkown type', type(data))
            ## End of While
            self._HB.terminate()
            if self._HB.isAlive():
                self._HB.join(timeout=5)
            self.stop_imagegenerator()
            print('Framesource: End')
        except Exception as e:
            print('Framesource Exception caught: %s'%(repr(e)))
            exc_type, exc_obj, tb = sys.exc_info()
            f = tb.tb_frame
            lineno = tb.tb_lineno 
            print('Framesource EXCEPTION IN (LINE {}): {}'.format(lineno, exc_obj))

            self._HB.set_update(e)
            if self._HB.isAlive():
                self._HB.join(timeout=5)
            raise e
        finally:
            self.stop_imagegenerator()
            pass

    def _camclient_connect(self, host, port):

        try:
            client  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host, port))            
            return client
        except socket.error as e:
            print("Unable to connect to the client: [%s]"%(repr(e)))
            raise e
            #return None

    def _camclient_thread(self, clientsock, inq, outq, reconst_done_event):

        readfds = [clientsock]
        exitthread = False 
        verbose = False

        totlen = 0
        count = 0
        length = None
        buf = b''

        data = b''
        msg=b''
        lasttime = time.time()
        meta = None
        totalbytes = 0

        msPkt = interface.CamServerFramePkt()

        print('Started client thread')
        while True:
            if exitthread:
                print("Framesource: Exiting _camclient thread")
                break;

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

            for s in infds:
                if s is clientsock:
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
                    if meta is None and datalen > msPkt.header_packet_size():
                        w, h, size, packetsize, ts, frameid, logging, gain, gain_min, gain_max, exposure, exposure_min, exposure_max, rate, rate_measured = msPkt.unpack_header(data)
                        meta = (w, h, size, packetsize, ts, frameid, logging, gain, gain_min, gain_max, exposure, exposure_min, exposure_max, rate, rate_measured)
                        totalbytes =  packetsize + msPkt.header_packet_size()
                        #if verbose:
                        if True:
                            #print('w=%d, h=%d, compval=%d, val=%d, size=%d, actualsize=%d, ts=%d, gain=%d, ccdtemp=%d', w, h, compval, val, size, actualsize, ts, gain, ccdtemp)
                            #print('w=%d, h=%d, size=%d, packetsize=%d, ts=%d, frameid=%d', w, h, size, packetsize, ts, frameid)
                            pass

                        if datalen >= totalbytes:  ### We have a complete packet stored.
                            msg = data[:totalbytes]
                            data = data[totalbytes:]
                            meta = None
                            totalbytes = 0
                            if verbose:
                                print('%.2f Hz'%(1/(time.time()-lasttime)))
                            lasttime = time.time()
                            count+=1
                            outq.put_nowait(msg)
                            if verbose:
                                print('%f: Full message received after getting meta: datalen=%d, datalen after=%d'%(time.time(), datalen, len(data)))
                    else:
                        if datalen < totalbytes:
                            continue

                        ### We have a complete message
                        msg = data[:totalbytes]
                        data = data[totalbytes:]
                        if verbose: print('%f: Full message received: datalen=%d, datalen after=%d'%(time.time(),datalen, len(data)))
                        meta = None
                        totalbytes = 0
                        ### Send frame here
                        outq.put_nowait(msg)
                        if verbose:
                            print('%.2f Hz'%(1/(time.time()-lasttime)))
                        lasttime = time.time()
                        count+=1
        print('Framesource:  End of Camera Client Thread')
        inq.queue.clear()
        self._meta.state = metadata_classes.Framesource_Metadata.FRAMESOURCE_STATE_IDLE
        self.publish_status()

   
if __name__ == '__main__':
    print('Main executed')
    import multiprocessing as mp
    import numpy as np
    import dhmpubsub as pubsub
    from dhmcommands import CommandDictionary
    img = interface.Image((1,2,3), np.zeros((2048,2048), dtype=np.float32))

  ### Create Message Queues
    ctx = mp.get_context('spawn')
    _qs = {}
    _qs['controller_inq']    = ctx.Queue()
    _qs['framesource_inq']   = ctx.Queue()
    _qs['reconstructor_inq'] = ctx.Queue()
    _qs['guiserver_inq']     = ctx.Queue()
    _qs['datalogger_inq']    = ctx.Queue()
    _qs['watchdog_inq']      = ctx.Queue()

    ### Make the publish/subscribe connections
    pub = pubsub.PubSub()
 
    #published by all modules to indicate that it is done initializing
    pub.subscribe('init_done', _qs['controller_inq'])

    # Subscribe to RAW FRAMES
    #pub.subscribe('rawframe', _qs['guiserver_inq'])
    pub.subscribe('rawframe', _qs['reconstructor_inq'])
    # Subscribe to RECONSTRUCTION PRODUCTS
    pub.subscribe('reconst_product', _qs['guiserver_inq'])

    pub.subscribe('reconst_done', _qs['framesource_inq'])
    pub.subscribe('reconst_done', _qs['controller_inq'])

    #-- Subscribe to STATUS messages
    #  Reconst Status
    pub.subscribe('reconst_status', _qs['controller_inq'])
    pub.subscribe('reconst_status', _qs['framesource_inq'])
    pub.subscribe('reconst_status', _qs['guiserver_inq'])
    #    Holo Status
    pub.subscribe('holo_status', _qs['controller_inq'])
    pub.subscribe('fouriermask_status', _qs['controller_inq'])
    pub.subscribe('session_status', _qs['controller_inq'])
    pub.subscribe('framesource_status', _qs['controller_inq'])
    pub.subscribe('datalogger_status', _qs['controller_inq'])
    pub.subscribe('guiserver_status', _qs['controller_inq'])
    pub.subscribe('watchdog_status', _qs['guiserver_inq'])
    # Subscribe to TELEMETRY messages
    #pub.subscribe('reconst_telemetry', _qs['guiserver_inq'])
    #pub.subscribe('holo_telemetry', _qs['guiserver_inq'])
    #pub.subscribe('fouriermask_telemetry', _qs['guiserver_inq'])
    #pub.subscribe('session_telemetry', _qs['guiserver_inq'])
    #pub.subscribe('framesource_telemetry', _qs['guiserver_inq'])
    #pub.subscribe('datalogger_telemetry', _qs['guiserver_inq'])
    #pub.subscribe('guiserver_telemetry', _qs['guiserver_inq'])
    #pub.subscribe('watchdog_telemetry', _qs['guiserver_inq'])
    # Subscribe to COMMAND messages
    pub.subscribe('dhm_cmd', _qs['controller_inq'])
    # Subscribe to HEARTBEAT messages
    pub.subscribe('heartbeat', _qs['watchdog_inq'])

    ### Create events
    _events = {}
    _events['reconst'] = {}
    _events['reconst']['done'] = ctx.Event()
    _events['controller'] = {}
    _events['controller']['start'] = ctx.Event()

    a = Framesource(_qs['framesource_inq'], pub, _events)
    a.start()
    _events['controller']['start'].set() ## Mimic the Controller
    count = 0
    _cmdDict = CommandDictionary()
    (cmd, statusstr) = _cmdDict.validate_command('framesource mode=file,exec=run')
    time.sleep(10)
    _qs['framesource_inq'].put_nowait(interface.Command(cmdobj=cmd))
    while count < 5:
        time.sleep(1)
        print('Count=%d'%(count))
        count += 1

    #pub.publish('rawframe',None)
    _qs['framesource_inq'].put_nowait(None)
    a.join()
    print('End of framesource main')
