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
    echo "-env        Environment setup"
    echo "-drivers    Install external drivers required."
    echo "-shampoo    Install Shampoo python module"
    echo "-camserver  Install camera server application software. Add '-drivers' if you don't have the drivers."
    echo "-dhmsw      Install DHM softwares python module"
    echo "-dhm_gui     Install DHM GUI and necessary packages"
    echo ""
    echo "any of the above options may be combined with any other"
    echo ""
    exit
}

create_install_location()
{
   INSTALL_ROOT=$1
   DHM_INSTALL_BIN=$INSTALL_ROOT/bin
   DHM_INSTALL_SRC=$INSTALL_ROOT/src
   DHM_INSTALL_CONFIG=$INSTALL_ROOT/config
   DHM_INSTALL_LOG=$INSTALL_ROOT/log

   if [ ! -f "$INSTALL_ROOT" ]; then
       mkdir /opt/DHM
   else
       echo "$INSTALL_ROOT already exists."
   fi

   if [ ! -f "$DHM_INSTALL_BIN" ]; then
       mkdir $DHM_INSTALL_BIN
   else
       echo "$DHM_INSTALL_BIN already exists."
   fi

   if [ ! -f "$DHM_INSTALL_SRC" ]; then
       mkdir $DHM_INSTALL_SRC
   else
       echo "$DHM_INSTALL_SRC already exists."
   fi

   if [ ! -f "$DHM_INSTALL_CONFIG" ]; then
       mkdir $DHM_INSTALL_CONFIG
   else
       echo "$DHM_INSTALL_CONFIG already exists."
   fi

   if [ ! -f "$DHM_INSTALL_LOG" ]; then
       mkdir $DHM_INSTALL_LOG
   else
       echo "$DHM_INSTALL_LOG already exists."
   fi

   chown -R $USER:dhm $DHM_INSTALL_ROOT
   
}

verbose=0
env_setup=0
drivers=0
shampoo=0
camserver=0
dhmsw=0
dhm_gui=0

DHM_INSTALL_ROOT=/opt/DHM
DHM_SUITE_DIR=$PWD
VIMBA_DRIVER_DIR=/opt/Vimba_3_0/
VIMBA_SDK_TARBALL=Vimba_v3.0_Linux.tgz

# Make -all default
if [ -z "$1" ]
then
        env_setup=1
        drivers=1
        shampoo=1
        camserver=1
        dhmsw=1
        dhm_gui=1
fi

### Parse command line options
while [ -n "$(echo $1 | grep '-')" ];
do
    case $1 in
    "-all")
        env_setup=1
        drivers=1
        shampoo=1
        camserver=1
        dhmsw=1
        dhm_gui=1
        ;;
    "-env")
        env_setup=1
        ;;
    "-verbose")
        verbose=1
        ;;
    "-drivers")
        drivers=1
        ;;
    "-shampoo")
        shampoo=1
        ;;
    "-camserver")
        camserver=1
        ;;
    "-dhmsw")
        dhmsw=1
        ;;
    "-dhm_gui")
        dhm_gui=1
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

printf "Options Selected: \n\tevn_setup=%s\n\tdrivers=%s\n\tshampoo=%s\n\tcamserver=%s\n\tdhmsw=%s\n\tdhm_gui=%s\n" $env_setup $drivers $shampoo $camserver $dhmsw $dhm_gui

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

if [ $env_setup -eq 1 ]
then

 apt-get update -y
 apt-get upgrade -y
 apt-get install -y build-essential
 apt-get install -y gcc g++
 apt-get install -y git
 apt-get install -y net-tools # for ifconfig
 apt-get install -y ethtool #
 apt-get install -y make
 apt-get install -y vim
 apt-get install -y libtiff5-dev
 apt-get install -y nautilus #for running shell scripts from desktop
 apt-get install -y xterm
 apt-get install -y exfat-fuse exfat-utils
 apt-get install -y python3-pip

 pip3 install --upgrade pip

 groupadd dhm
 usermod -aG dhm $USER
 #create_install_location $DHM_INSTALL_ROOT



fi

if [ $drivers -eq 1 ]
then
  ### Install Vimba driver
  ## Check if /opt/Vimba
  if [ ! -d "$VIMBA_DRIVER_DIR" ]; then
       tar -xvzf $DHM_SUITE_DIR/drivers/$VIMBA_SDK_TARBALL -C /opt/
       ## Install tranport layers
       echo "Installing Vimbal GigE and USB transport layers..."
       $VIMBA_DRIVER_DIR/VimbaGigETL/Install.sh
       $VIMBA_DRIVER_DIR/VimbaUSBTL/Install.sh
       echo "Creating VimbaViewer shortcut on the Desktop..."
       ln -s $VIMBA_DRIVER_DIR/Tools/Viewer/Bin/x86_64bit/VimbaViewer ~/Desktop/.
  else
      echo "Vimba driver directory [$VIMBA_DRIVER_DIR] exists! Skipping this driver install."
  fi



fi

if [ $shampoo -eq 1 ]
then
### Install shampoo
pip3 install astropy-helpers
cd $DHM_SUITE_DIR/shampoo
python3 setup.py install

fi

if [ $camserver -eq 1 ]
then
make clean -C $DHM_SUITE_DIR/camserver; make -C $DHM_SUITE_DIR/camserver
chmod 777 $DHM_SUITE_DIR/camserver/bin/camserver
cp $DHM_SUITE_DIR/camserver/bin/* $DHM_SUITE_DIR/bin/.
fi

if [ $dhmsw -eq 1 ]
then
cd $DHM_SUITE_DIR/dhmsw
python3 setup.py install
fi

if [ $dhm_gui -eq 1 ]
then
cd $DHM_SUITE_DIR/dhm_gui/tools/
./Setup
cp -rf $DHM_SUITE_DIR/dhm_gui $DHM_INSTALL_ROOT/src/.
fi

if [ ! -e $DHM_INSTALL_ROOT ]; then
	echo "Creating $DHM_INSTALL_ROOT..."
	mkdir $DHM_INSTALL_ROOT
	chown -R $USER:dhm $DHM_INSTALL_ROOT
fi

echo "Copying contents of directory into $DHM_INSTALL_ROOT..."
rsync -av --progress $DHM_SUITE_DIR/ $DHM_INSTALL_ROOT --exclude $DHM_SUITE_DIR/.git

echo " * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"
echo " *"
echo " *"
echo " *"
echo " *                     DHM Software Suite Installer has completed "
echo " *"
echo " *"
echo " * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"
