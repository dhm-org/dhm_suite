# Laser-Pulse-Controller (aka TriggerBox)
This was meant to be a simple, terminal-based program to interact with the LPC blue boxes via the USB serial port.
It was orignially developed under Windows, within a Python 3.56 installation.
Additionally, two windows upport packages were added, pywin32-224.win-amd64-py3.5.exe, and PySerial-3.4. I have included these
in the zipped file 'WindowsPythonPackages.zip' which should work with a Windows Python 3.5.6 installation.

At this writing I cannot guarantee that there is equivalent functionality within the Linux environment. I'm confident
that the code could be ported, but I'm not sure how much effort is involved.

The main code body is called 'startLaserPulseController.py', and uses the class 'laserPulseController.py' to do most of
the heavy lifting. It employs much of the PySerial functions, as well as some 'fancy pants' COM port discovery calls that
may be specific to pyWin32. I know I had install that module to get the 'keyboard.kbhit()' function. Hopefully there are Linux
analogs.

So if you can compile 'startLaserPulseController.py', then you should be close. In Windows, you just have to plug the Blue box
into any USB port, and it should find it.
