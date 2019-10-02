# Laser-Pulse-Controller Version 3

This version of 'startLaserPulseController' contains two main updates:
1) External Trigger options added to menu.
2) Program can now run copies of itself for each plugged-in trigger box.

A box can be placed in external trigger mode. This means another clock source can cause a clock burst out of that box. This gives the
user the ability to make more clock pulses with their own pulse width and phase with respect to the trigger input. 

For multiple instances to work all of the trigger boxes must be plugged-in, a USB3 extention hub
works fine. When starting the program for the first trigger box, type either python3 startLaserPulseController3.py 0,
or just python3 startLaserPulseController3.py (when no index is present, it defaults to 0). To start for second trigger
box, type: python3 startLaserPulseController3.py 1. This will work for as many boxes one can plug in, Each instance requires
its own configuration file. The filenames look like lpc_set3.0, lpc_set3.1, lpc_set3.2, lpc_set3.3 etc. There must be configuration
file for every box plugged in. If for example, you have 5 boxes, then lpc_set3.4 must exist! One can easily create one by copying
an existing file into a new one with the new file name. This approach seemed better than having several program instances trying to
access the same file! The config files are stored in the directory where the program executes.
