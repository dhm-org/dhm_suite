import sys
from laserPulseController import *
if sys.platform == 'win32':
    import msvcrt as keyboard
else:
    import keyboard
import time

def showMenu():
	print('<------------------------(Options)-------------------------->')
	print(' f <freq>       : Set Frequency in Hz')
	print(' c <width>      : Set Clock A Pulsewidth in usec')
	print(' w <width>      : Set clock B Pulsewidth in usec')
	print(' a <width>      : Set Clock C Pulsewidth in usec')
	print(' p <phase>      : Set Clock A-to-B Phase Offset in usec')
	print(' u <width>      : Set Clock A-to-C Phase Offset in usec')
	print(' v <width>      : Set Clock B Modulus')
	print(' x <mod>        : Set Clock C Modulus')
	print(' i              : Set Clock Burst Count');
	print(' y              : Enable Clock Burst Mode')
	print(' z              : Disable Clock Burst Mode')
	print(' g              : Manually Start Clocks')
	print(' h              : Manually Stop Clocks')
	
	
	print(' d              : Display Current Settings')
	print(' m              : Display this Menu')
	print(' b              : Back up Current Settings')
	print(' l              : Load Backed up Settings')
	print(' r              : Set to Free Run Mode')
	print(' e              : Set to External Trigger Mode')
	print(' t <"on","off"> : Enable/Disable External Trigger')
	print(' s <"hi","lo">  : Set External Trigger Sense')
	print(' q              : Quit\r\n')

def displayCurrentSettings(lpc_ob):
	print('\n')
	print('<--(Current Settings)-->')
	print('Frequency      =',lpc_ob.currentFrequency)
	print('PulsewidthA    =',lpc_ob.currentPulsewidthA)
	print('PulsewidthB    =',lpc_ob.currentPulsewidthB)
	print('PulsewidthC    =',lpc_ob.currentPulsewidthC)
	print('ModulusB       =',lpc_ob.currentModulusB)
	print('ModulusC       =',lpc_ob.currentModulusC)
	print('ClockAtoBdelay =',lpc_ob.currentAtoBdelay)
	print('ClockAtoCdelay =',lpc_ob.currentAtoCdelay)
	print('ClockRunState  =',lpc_ob.currentRunState)
	print('BurstModeEnabled =',lpc_ob.currentCountdownState)
	print('BurstCount       =',lpc_ob.currentCountdown)
	print('ExternalTriggerEnabled =',lpc_ob.currentExternalInterruptState)
	print('ExternalTriggerPolarity =',lpc_ob.currentInterruptSense)
	print('Device Instance =',lpc_ob.deviceInstance)
	
	print('\n')
	
def loadBackupSettings(lpc_ob):
	fn = "lpc.set3." + str(lpc_ob.deviceInstance)
	df = open(fn,'r')
	lpc_ob.currentFrequency   = float(df.readline())
	lpc_ob.currentPulsewidthA = int(df.readline())
	lpc_ob.currentPulsewidthB = int(df.readline())
	lpc_ob.currentPulsewidthC = int(df.readline())
	lpc_ob.currentModulusC    = int(df.readline())
	lpc_ob.currentAtoBdelay   = int(df.readline())
	lpc_ob.currentAtoCdelay   = int(df.readline())
	lpc_ob.currentRunState    = int(df.readline())
	
	lpc_ob.currentModulusB               = int(df.readline())
	lpc_ob.currentCountdown              = int(df.readline())
	lpc_ob.currentCountdownState         = int(df.readline())
	lpc_ob.currentExternalInterruptState = int(df.readline())
	lpc_ob.currentInterruptSense         = int(df.readline())
	df.close()
	
	lpc_ob.setFrequency(lpc_ob.currentFrequency)
	lpc_ob.setPulsewidthA(lpc_ob.currentPulsewidthA)
	lpc_ob.setPulsewidthB(lpc_ob.currentPulsewidthB)
	lpc_ob.setPulsewidthC(lpc_ob.currentPulsewidthC)
	lpc_ob.setModulusB(lpc_ob.currentModulusB)
	lpc_ob.setModulusC(lpc_ob.currentModulusC)
	lpc_ob.setClockAtoBdelay(lpc_ob.currentAtoBdelay)
	lpc_ob.setClockAtoCdelay(lpc_ob.currentAtoCdelay)
	lpc_ob.setCountdown(lpc_ob.currentCountdown)
	
	if lpc_ob.currentCountdownState == 1:
		lpc_ob.enableClocksCountdown()
	else:
		lpc_ob.disableClocksCountdown()
    		
	if lpc_ob.currentExternalInterruptState == 1:
		lpc.enableExternalTrigger()
	else:
		lpc.disableExternalTrigger()
		
	if lpc_ob.currentInterruptSense == 1:
		lpc.setExternalInterruptSense(1)
	else:
		lpc.setExternalInterruptSense(0)
		
	if lpc_ob.currentRunState == 1:
		lpc_ob.startClocks()
	else:
		lpc_ob.stopClocks()	

def backupCurrentSettings(lpc_ob):
	fn = "lpc.set3." + str(lpc_ob.deviceInstance)
	df = open(fn,'w')
	df.write(str(lpc_ob.currentFrequency)+'\n')
	df.write(str(lpc_ob.currentPulsewidthA)+'\n')
	df.write(str(lpc_ob.currentPulsewidthB)+'\n')
	df.write(str(lpc_ob.currentPulsewidthC)+'\n')
	df.write(str(lpc_ob.currentModulusC)+'\n')
	df.write(str(lpc_ob.currentAtoBdelay)+'\n')
	df.write(str(lpc_ob.currentAtoCdelay)+'\n')
	df.write(str(lpc_ob.currentRunState)+'\n')
	df.write(str(lpc_ob.currentModulusB)+'\n')
	df.write(str(lpc_ob.currentCountdown)+'\n')
	df.write(str(lpc_ob.currentCountdownState)+'\n')
	df.write(str(lpc_ob.currentExternalInterruptState)+'\n')
	df.write(str(lpc_ob.currentInterruptSense)+'\n')
	df.close()

# Clear the screen
print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')

if len(sys.argv) > 1: 
	lpc = laserPulseController(int(sys.argv[1]))
else:
	lpc = laserPulseController()
lpc.open()

inApp = 5
if lpc.port_found:
	print('\nDHM Laser Pulse Controller Tool\r\n')
	# Set to deterministic clocks from the get go	
	lpc.setProbabilityA(1.0)
	lpc.setProbabilityB(1.0)
	lpc.disableClocksCountdown()
	lpc.disableExternalTrigger()
	loadBackupSettings(lpc)
	displayCurrentSettings(lpc)
	showMenu()
	print('=> ',end='',flush=True)
else: # Shutdown after 5 seconds
	while inApp > 0:
		time.sleep(1)
		inApp -= 1

while inApp:
	if keyboard.kbhit():
		while 1:
			keyin = keyboard.getch()
			if keyin.isalnum():
                            if sys.platform == 'win32':
                                key = keyin.decode('ASCII')
                            else:
                                key = keyin
                            break
		print(key,end='',flush=True)
		if key == 'q':
			inApp = 0
		elif key == 'f':
			data = input(': Enter Frequency (Hz) => ')
			lpc.setFrequency(float(data))
		elif key == 'i':
			data = input(': Set Clock Burst Count => ')
			lpc.setCountdown(int(data))
		elif key == 'w':
			data = input(': Enter Clock B Pulse Width (Usec) => ')
			lpc.setPulsewidthB(int(data))
		elif key == 'c':
			data = input(': Enter Clock A Pulse Width (Usec) => ')
			lpc.setPulsewidthA(int(data))
		elif key == 'a':
			data = input(': Enter Clock C Pulse Width (Usec) => ')
			lpc.setPulsewidthC(int(data))	
		elif key == 'p':
			data = input(': Enter Clocks A-to-B Phase Offset (Usec) => ')
			lpc.setClockAtoBdelay(int(data))
		elif key == 'u':
			data = input(': Enter Clocks A-to-C Phase Offset (Usec) => ')
			lpc.setClockAtoCdelay(int(data))
		elif key == 'v':
			data = input(': Enter Clock B Modulus => ')
			lpc.setModulusB(int(data))			
		elif key == 'x':
			data = input(': Enter Clock C Modulus => ')
			lpc.setModulusC(int(data))
			
		elif key == 't':
			data = input(': Enter External Trigger on/off => ')
			if data == 'on':
				lpc.enableExternalTrigger()
			if data == 'off':
				lpc.disableExternalTrigger()
		elif key == 's':
			data = input(': Enter External Trigger Sense hi/lo => ')
			if data == 'hi':
				lpc.setExternalInterruptSense(1)
			if data == 'lo':
				lpc.setExternalInterruptSense(0)
		elif key == 'r':
			lpc.disableClocksCountdown()
			lpc.disableExternalTrigger()
			lpc.startClocks()
			print(' : Now in Free Run Mode')
		elif key == 'e':
			lpc.stopClocks()
			lpc.setCountdown(1)	
			lpc.enableClocksCountdown()
			lpc.enableExternalTrigger()
			print(' : Now in External Trigger Mode')
		elif key == 'd':
			lpc.updateCurrentSettings()
			displayCurrentSettings(lpc)
		elif key == 'm':
			print('')
			showMenu()
		elif key == 'b':
			lpc.updateCurrentSettings()
			backupCurrentSettings(lpc)
			print(' : Current Settings Backed Up')
			displayCurrentSettings(lpc)
		elif key == 'l':
			print(' : Backup Settings Loaded')
			loadBackupSettings(lpc)
			displayCurrentSettings(lpc)
		elif key == 'g':
			lpc.startClocks()
			print(' : Clocks Started')
		elif key == 'h':
			lpc.stopClocks()
			print(' : Clocks Stopped')
		elif key == 'y':	
			lpc.enableClocksCountdown()
			print(' : Burst Mode Enabled')
		elif key == 'z':
			lpc.disableClocksCountdown()
			print(' : Burst Mode Disabled')				
		else:
			print('')
			showMenu()
		print('=> ',end='',flush=True)
			
			



