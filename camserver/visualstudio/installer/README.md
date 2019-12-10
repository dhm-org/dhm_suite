This is the Windows version of the DHM Camera Server,
currently coded to support Allied Vision Cameras.

Everything (except Vimba) is contained within setup.exe
This version has been tested with Vimba 3.0 and Vimba 3.1.

It is still necessary for the user to install and configure
Vimba. A good test would be to see if Vimba Viewer will run
properly. If it doesn't, then most likely you have
a GigE camera, and you need to configure your GigE
related settings (packet filter, ip, etc.). This is
covered in the Vimba GiGe Features Reference (document
should be in the Windows startup Menu).

After installation, a shortcut labeled 'DhmCameraServer'
will appear. This shortcut simply starts DhmCameraServer.exe
with no arguments. This can be edited as the user sees fit,
bearing in mind that any additional arguments must comply
with what is supported. If in doubt, from a terminal window
enter 'DhmCameraServer.exe -h'


