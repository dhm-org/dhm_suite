#!/bin/bash
###############################################################################
#  File:   setup_networkiface.sh
#
#  Brief:  Append lines to /etc/network/interface which will allow communication
#          with GigE camera.
#
#  Description:  Append lines to the /etc/network/interface file which setup
#                the following to the user selected network interface.
#                    IP Address:  169.254.100.1
#                    Netmask: 255.255.0.0
#                Some network parameters may not be compatible with the selected
#                ethernet interface but the following will be attempted and if
#                successful they will be added:
#                    MTU 900
#                    Speed 1000; Duplex FULL; Autonegotiation OFF
#                    Receive buffers 4096; Transmit buffers 256
#
#                NOTE:  The current /etc/network/interface file is renamed to:
#                       /etc/network/interface_<date in seconds>
#
#  Requirements:  - Run this script with sudo powers
#  
###############################################################################

IP_ADDRESS_DEFAULT=169.254.100.1
NETMASK_DEFAULT=255.255.0.0

networkiface_entries()
{
    netiface=$1
    ipaddress=$2
    netmask=$3

    STR="\n"
    STR="${STR}auto $netiface\n"
    STR="${STR}iface $netiface inet static\n"
    STR="${STR}address $ipaddress\n"
    STR="${STR}netmask $netmask\n"

    ###
    # NOTE:  The following parameters may not be compatible depending on the drivers
    #        The command is attempted and if works, then added to file, else not.
    # Set MTU to 9000
    /sbin/ifconfig $netiface mtu 9000 > /dev/null 2>&1
    if [ $? -eq 0]; then
	STR="${STR}mtu 9000\n"
    fi

    /sbin/ethtool -s $netiface speed 1000 duplex full autoneg off > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        STR="${STR}/sbin/ethtool -s $netiface speed 1000 duplex full autoneg off\n"
    fi

    /sbin/ethtool -G $netiface rx 4096 tx 256 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
	STR="${STR}/sbin/ethtool -G $netiface rx 4096 tx 256\n"
    fi
    STR="${STR}\n"
    ###

    # Copy existing network interface and rename
    EPOCH_TIME_SEC=`date +%s`

    cp /etc/network/interfaces /etc/network/interfaces_$EPOCH_TIME_SEC

    echo -e $STR >> /etc/network/interfaces

    echo "*** The following lines were appended to file:  /etc/network/interfaces ***"
    echo -e $STR

}

### Ensure script is run with SUDO powers to append strings to network file
if [ "$EUID" -ne 0 ]
then
    echo "Please run this environment setup using sudo or as root"
    exit
fi

### Get network interfaces into an array
array_test=()
for iface in $(ifconfig | cut -d ' ' -f1| tr ':' '\n' | awk NF)
do
        array_test+=("$iface")
done


echo "************************************************************************"
echo "***     Setup Network Interfaces for Allied Vision GigE Camera Use     *"
echo "************************************************************************"

echo "Select network interface where GigE camera will be plugged into:"
echo ""
for ((i=1; i <= ${#array_test[@]}; i++)); do echo "$i) ${array_test[$i-1]}"; done
echo ""


### Get user input to select network interface
while [ 1 ]
do
    read -p "Enter selection number and press [ENTER]: " selection

    re='^[0-9]+$'
    if ! [[ $selection =~ $re ]] ; then
	    echo "    Error:  User input must be an integer number.  Try again."
	    continue
    fi

    if [ $selection -ge 1 ] && [ $selection -le ${#array_test[@]} ]; then
	    user_selection=$selection-1
	    break
    else
	    echo "Selection not valid."
    fi

done

### Get user input to enter IP address
while [ 1 ]
do
    read -p "Enter ip address and press [ENTER] (default $IP_ADDRESS_DEFAULT): " user_ip_address

    if [ -z "$user_ip_address" ] ; then
	    IP_ADDRESS=$IP_ADDRESS_DEFAULT
    else
	    IP_ADDRESS=$user_ip_address
    fi

    break

done

### Get user input to set Netmask
while [ 1 ]
do
    read -p "Enter netmask and press [ENTER] (default $NETMASK_DEFAULT): " user_netmask

    if [ -z "$user_netmask" ] ; then
	    NETMASK=$NETMASK_DEFAULT
    else
	    NETMASK=$user_netmask
    fi

    break

done

echo ""
networkiface_entries ${array_test[$user_selection]} $IP_ADDRESS $NETMASK

