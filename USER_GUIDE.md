# Digital Holographic Microscope Software Suite User Manual
Assuming installation of the software was successful, the following instructions should get you working.

# Quick Start
This quick start describes instructions to run the DHMx components on a single (the same) system.
In order to run any of the components on different systems, such as the camserver on one system
and the DHMx GUI on another, the IP address must be specified.  See
the components usage on how to do that.

## Start Camserver
To start the camserver with logging initially disabled (-d), verbose enabled and
logging data to the desktop, issue the following command from a terminal.

`/opt/DHM/bin/camserver -d -v -l ~/Desktop/`

## Start Camera GUI (DHMx-C)
Pre-requisite:  Ensure the camserver is running.  The Camera GUI will poll at 1Hz for a connection 
if it can't find the camserver.

To start the camera GUI, you need to run the following script from the containing directory.
From a terminal, do the following:

`cd /opt/DHM/dhm_gui/`
`python3 dhmxc.py`

The camera GUI should appear.

## Start the DHMx GUI to View Images and Reconstruction Products
NOTE:  The camserver doesn't need to be running if you plan on reconstructing images on file.

First, we need to run the 'dhmsw' software which is the the software the receives the images and performs the reconstruction. 
Open a terminal and run the following:

`python3 -m dhmsw.main`

Now open another terminal and run the following:

`cd /opt/DHM/dhm_gui/`
`python3 dhmx.py`

![DHMx GUI](doc/dhmx_gui_screenshot.jpeg)


