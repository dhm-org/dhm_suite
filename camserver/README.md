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

## Configure Network Card
The following steps are for configuring your network card so that the camserver (and VimbaViewer)
can see the camera.

NOTE:  These instructions expect one GigE camera per network card.  Use of a switch is not supported

NOTE:  Ensure the camera is plugged into the network card and powered up.
### One GigaE Camera Per System
1.  Open terminal
2.  Enter the following:  
    * ifconfig
3.  Identify which ethernet adapter you want to configure.  Typical names start with 'eth' or 'enp'
4.  Open the following file with sudo privledges.  This example uses the 'vi' editor.
    * sudo vi /etc/network/interfaces
5.  Enter the following lines were you replace "<network_card_name>" with the name from Step 3.
    * auto <network_card_name>
    * iface <nework_card_name> inet static
    * address 192.168.100.1
    * netmask 255.255.0.0
    * mtu 9000
    * pre-up /sbin/ethtool -s <network_card_name> speed 1000 duplex full autoneg off
6.  Save the file and close
7.  Reboot the system
8.  Once boot up, open the 'VimbaViewer' to verify that the camera can be seen.
    * If you see the camera listed then SUCCESS!
    * If you don't see it possibly due to the following:
        - You configured a different network card then the one the camera is connected to.  Try connecting to 
          another card and wait a few seconds for the VimbaViewer to list the camera
        - The camera is not powered on.
        - The driver install of the Vimba drivers did not run 'VimbaGigETL/Install.sh'.  Do so manually and reboot.

### Two or More GigaE Camera Per System
These instructions require that one camera per network card.

NOTE:  This method assume you know the IP addresses of each of the cameras you will be using. 
If you don't know the IP addresses of the cameras, follow the 'One GigE Camera Per System' instructions
and connect each camera to the network card configured and write down each IP address.

NOTE:  This method ties a camera to a specific network card.

NOTE:  Let's assume I am connecting two cameras with the following IP address: 192.168.225.50 and 192.168.48.3.

1.  Open terminal
2.  Enter the following:  
    * ifconfig
3.  Identify which ethernet adapter you want to configure.  Typical names start with 'eth' or 'enp'
4.  Open the following file with sudo privledges.  This example uses the 'vi' editor.
    * sudo vi /etc/network/interfaces
5.  Enter the following lines were you replace "<network_card_name>" with the name from Step 3.
    Note that I'm using the IP address for our example.
    * auto <network_card_name>
    * iface <nework_card_name> inet static
    * address x.x.x.1  # Replace the x with the associated numbers
    * netmask 255.255.255.0
    * mtu 9000
    * pre-up /sbin/ethtool -s <network_card_name> speed 1000 duplex full autoneg off
6.  Repeat Step 5 and add another set of the instructions using the other network card and the other IP address.
7.  Save the file and close
8.  Reboot the system
9.  Once boot up, open the 'VimbaViewer' to verify that the cameras can be seen.
    * If you see the cameras listed then SUCCESS!
    * If you don't see it possibly due to the following:
        - You configured a different network card then the one the camera is connected to.  Try connecting to 
          another card and wait a few seconds for the VimbaViewer to list the camera
        - The camera is not powered on.
        - The driver install of the Vimba drivers did not run 'VimbaGigETL/Install.sh'.  Do so manually and reboot.


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


