#!/bin/bash
###############################################################################
#  file:   install.sh
#  brief:  This is the DHM Software Suite install script
#  author:  Santos F. Fregoso
#  date:    05/29/2019
###############################################################################

usage() 
{
    echo ""
    echo "usage:  install.sh [options]"
    echo ""
    echo "where options are as follows:"
    echo "-all        Setup environment, install drivers, and install suite software"
    echo "-verbose    Display instruction verbose to standard out"
    echo ""
    echo "any of the above options may be combined with any other"
    echo ""
    exit
}

env_setup=0
drivers=0
suite=0

DHM_SUITE_DIR=$PWD
VIMBA_DRIVER_DIR=/opt/Vimba_2_1/

### Parse command line options
while [ -n "$(echo $1 | grep '-')" ];
do
    case $1 in
    "-all")
        env_setup=1
        drivers=1
        suite=1
        ;;
    "-env_setup")
        env_setup=1
        ;;
    "-verbose")
        verbose=1
        ;;
    "-drivers")
        drivers=1
        ;;
    "-suite")
        suite=1
        ;;
    "-help")
        usage
        ;;
    *)
        usage
        ;;
    esac
    shift
done

if [ "$EUID" -ne 0 ]
then
    echo "Please run this environment setup using sudo or as root"
    exit
fi

clear
echo "* * * * * * * * * * * * DHM Software Suite Installer * * * * * * * * * *"
echo "This environment was tested to be used for Ubuntu 18.04 OS"
echo "If you do not have Ubuntu 18.04, either exit or proceed with caution"
echo ""
echo "NOTE: Please ensure that you have an active internet connection in order"
echo "      to download necessary files that this environment installer "
echo "      requires."
echo "* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"
echo ""
read -r -p "Do you want to continue? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY])
        ;;
    *)
        exit
        ;;
esac

if [ "$env_setup" ]
then

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install -y build-essential
sudo apt-get install -y gcc
sudo apt-get install -y git
sudo apt-get install -y net-tools # for ifconfig
sudo apt-get install -y ethtool #
sudo apt-get install -y make
sudo apt-get install -y vim
sudo apt-get install -y libtiff5-dev
sudo apt-get install -y nautilus #for running shell scripts from desktop
sudo apt-get install -y xterm
sudo apt-get install -y exfat-fuse exfat-utils

fi

if [ "$drivers" ]
then
  ### Install Vimba driver
  ## Check if /opt/Vimba
  if [ ! -d "$VIMBA_DRIVER_DIR" ]; then
      sudo tar -xvzf ./drivers/Vimba_v2.1.3_Linux.tgz -C /opt/
  
      ## Install tranport layers
      echo "Installing Vimbal GigE and USB transport layers..."
      sudo /opt/Vimba_2_1/VimbaGigETL/Install.sh
      sudo /opt/Vimba_2_1/VimbaUSBTL/Install.sh
  else
      echo "Vimba driver directory [$VIMBA_DRIVER_DIR] exists! Skipping this driver install."
  fi

fi

if [ "$suite" ]
then
### Install shampoo
cd $DHM_SUITE_DIR/shampoo
python3 setup.py install

### Install dhmsw

### Install dhm_gui
#cd $DHM_SUITE_DIR/dhm_gui/tools
#./Setup

fi


