from laserPulseController import *
lpc = laserPulseController()
lpc.open()
if lpc.port_found: lpc.freeRun(200,1000,2000,1500)
