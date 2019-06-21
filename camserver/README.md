# camserver - Camera server for Allied Vision USB and GigE Cameras
Camera Server for Allied Vision cameras (USB and GigE cameras only)

## Description
The camserver software has the following features for a single camera per execution:

*  Asynchronous capture of frames
*  Works with Allied Vision cameras ONLY using the Allied Vision Vimba Driver
*  Record camera frames as TIF files to disk.  Creates daily directory and run directory with timestamp file and camera metadata file.
*  Send camera files to connected clients at 6Hz
*  Receive commands via command socket
*  Send telemetry via telemetry socket (Not yet implemented)
*  Specify execution time via command line option

## Prerequisite:  
* 64-bit Linux Operating System.
* Tested on Ubuntu 16.04, 18.04, and Redhat 7.
* 16GB RAM or greater
* For GigaE Cameras
  - Network card configured per [Allied Vision](https://www.alliedvision.com/fileadmin/content/documents/products/cameras/various/installation-manual/GigE_Installation_Manual.pdf) recomendations.
  - USB3 to Ethernet or USB-C to Ethernet adapters tested.
  - NOTE:  Ensure that you are using the proper drivers for the network card.  Linux will use
    generic drivers which don't always give you access to card's full functionality such as
    setting the receive buffers or setting the interrupt modulation rate.
* Drivers
  -  Install the VIMBA driver on your machine.  You can download from [here](https://www.alliedvision.com/en/products/software.html)
, download from this repository 'drivers' directory, or run 'install.sh -drivers' located in root of this repository. 
  -  Run the 'VimbaGigETL/Install.sh' for GigE cameras or the 'VimbaUSBTL/Install.sh' for USB cameras.

## Compiling code
Modify the make file so that is contains the proper path the to the VIMBA SDK directory

## Cameras tested with camserver
* Mako U-503B (USB3 camera)
* GT 2460 (GigE camera)
* Manta G201B ASG 30fps (GigE camera)

## Reading from Two Cameras
To read from two cameras, two instances of 'camserver' must be executed making sure the following:
*  Distinct cameras are selected for each instance
*  If expect to connect clients, ensure distinct port number are passed on the command line on execution.
*  Recommended that if using two GigE cameras, each one be connected to a single
 
## Frame Server/Client
Frames are sent to client at 6Hz or less if frame rate is less than 6H.  Clients must connect to the frame port
(default port 2000, see usage for setting frame port).

## Commanding
Commanding occurs via the command port (default command port is 2001, see usage for setting port).
The command client connection is active only for accepting the command and returning an acknowledgment, then the server closes the connection.
* Implemented commands see [CamCommands.h](include/CamCommands.h)
  - The command are case sensitive and expects no spaces between equal signs.

## Telemetry
As of version 0.5.0, sending telemetry to clients not implemented.
Once implemented, clients must connect to the telemetry port (default telemetry port is 2002, see usage for setting port).

## Graphical User Interface
The python3 script 'dhmxc.py' in the 'dhm_gui' directory of this repository is the GUI for the camserver.
For each instances of the camserver, ensure that the frame port, command port, and telemetry port
specified in the camserver are also the same psecified when running the 'dhmxc.py' script.

## Known Bugs
* With USB cameras, sometimes the frame capture doesn't start.  Stop the camserver using
  Ctrl-C then restart again and camserver will begin to capture frames.
* With USB cameras sometimes some initialization commands tend to error out but they in fact get executed.
  See the 'metadata.xml' created when recording frames.


