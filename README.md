# Digital Holographic Microscope Software Suite

##  Operating System Requirement
*  Ubuntu 16.04 or greater 64-bit
   -  The software was designed for Linux system particularity Ubuntu.
   -  Tested also on Redhat 7 Linux

##  Minimum System Requirements
Testing has been successful on a system with the following requirements

* Processor
  -  Tested on 3.7GHz, 8MB Cache, 4-core system
* RAM Memory
  -  16GB minimum but 32GB or greater recommended
* Hard Disk
  -  4GB minimum
* Other Hardware
  -  For GigE Cameras.  Network card recommended by the [Allied vision](https://www.alliedvision.com/fileadmin/content/documents/products/cameras/various/installation-manual/GigE_Installation_Manual.pdf) or one that supports 
     jumbo packets of 9000 bytes or more, 1Gbps bandwidth.
     -  Configure Netword card per Allied Vision recommendations for optimal performance
     -  See [camserver README.md](camserver/README.md) for instructions to configure network card
        to read one or more cameras.
  -  USB3 and/or USB-C Ports
     -  Best for USB to Ethernet adapters

## Installation Instruction
With 'sudo' powers, run 'install.sh -all' to setup the environment, install drivers, and install the dhm software.

This install script has options in case you want to do a step at a time.  The following order is recommended

* Installation location
  - Install script will copy contents of this repo into /opt/DHM/

