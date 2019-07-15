from laserPulseController import *
import msvcrt as keyboard
import time


def showMenu():
	print('<------------------------(Options)-------------------------->')
	print(' f <freq>       : Set Frequency in Hz')
	print(' w <width>      : Set Laser Pulse (clock B) width in usec')
	print(' c <width>      : Set Camera Trigger Pulse (clock A) width in usec')
	print(' p <phase>      : Set Trigger-to-Laser Phase Offset in usec')
	print(' a <width>      : Set Auxillary (clock C) pulsewidth in usec')
	print(' u <width>      : Set Trigger-to-Aux (clock C) Phase Offset in usec')
	print(' x <width>      : Set Aux (clock C) Modulus')
	print(' t <"on","off"> : Enable/Disable External Trigger')
	print(' s <"hi","lo">  : Set External Trigger Sense')
	print(' g              : Manually Start Clocks')
	print(' h              : Manually Stop Clocks')
	print(' r              : Set to Free Run Mode')
	print(' e              : Set to External Trigger Mode')
	print(' d              : Display Current Settings')
	print(' m              : Display this menu')
	print(' b              : Back up Current Settings')
	print(' l              : Load Backed up Settings')
	print(' q              : Quit\r\n')

def displayCurrentSettings(lpc_ob):
	print('\n')
	print('<--(Current Settings)-->')
	print('Frequency      =',lpc_ob.currentFrequency)
	print('PulsewidthA    =',lpc_ob.currentPulsewidthA)
	print('PulsewidthB    =',lpc_ob.currentPulsewidthB)
	print('PulsewidthC    =',lpc_ob.currentPulsewidthC)
	print('ModulusC       =',lpc_ob.currentModulusC)
	print('ClockAtoBdelay =',lpc_ob.currentAtoBdelay)
	print('ClockAtoCdelay =',lpc_ob.currentAtoCdelay)
	print('ClockRunState  =',lpc_ob.currentRunState)
	print('\n')
	
def loadBackupSettings(lpc_ob):
	df = open("lpc.set",'r')
	lpc_ob.currentFrequency   = float(df.readline())
	lpc_ob.currentPulsewidthA = int(df.readline())
	lpc_ob.currentPulsewidthB = int(df.readline())
	lpc_ob.currentPulsewidthC = int(df.readline())
	lpc_ob.currentModulusC    = int(df.readline())
	lpc_ob.currentAtoBdelay   = int(df.readline())
	lpc_ob.currentAtoCdelay   = int(df.readline())
	lpc_ob.currentRunState    = int(df.readline())
	df.close()
	lpc_ob.setFrequency(lpc_ob.currentFrequency)
	lpc_ob.setPulsewidthA(lpc_ob.currentPulsewidthA)
	lpc_ob.setPulsewidthB(lpc_ob.currentPulsewidthB)
	lpc_ob.setPulsewidthC(lpc_ob.currentPulsewidthC)
	lpc_ob.setModulusC(lpc_ob.currentModulusC)
	lpc_ob.setClockAtoBdelay(lpc_ob.currentAtoBdelay)
	lpc_ob.setClockAtoCdelay(lpc_ob.currentAtoCdelay)
	if lpc_ob.currentRunState == 1:
		lpc_ob.startClocks()
	else:
		lpc_ob.stopClocks()	

def backupCurrentSettings(lpc_ob):
	df = open("lpc.set",'w')
	df.write(str(lpc_ob.currentFrequency)+'\n')
	df.write(str(lpc_ob.currentPulsewidthA)+'\n')
	df.write(str(lpc_ob.currentPulsewidthB)+'\n')
	df.write(str(lpc_ob.currentPulsewidthC)+'\n')
	df.write(str(lpc_ob.currentModulusC)+'\n')
	df.write(str(lpc_ob.currentAtoBdelay)+'\n')
	df.write(str(lpc_ob.currentAtoCdelay)+'\n')
	df.write(str(lpc_ob.currentRunState)+'\n')
	df.close()

# Clear the screen
print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')

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
				key = keyin.decode('ASCII')
				break
		print(key,end='',flush=True)
		if key == 'q':
			inApp = 0
		elif key == 'f':
			data = input(': Enter Frequency (Hz) => ')
			lpc.setFrequency(float(data))
		elif key == 'w':
			data = input(': Enter Laser Pulse Width (Usec) => ')
			lpc.setPulsewidthB(int(data))
		elif key == 'c':
			data = input(': Enter Camera Trigger Pulse Width (Usec) => ')
			lpc.setPulsewidthA(int(data))
		elif key == 'a':
			data = input(': Enter Auxillary Pulse Width (Usec) => ')
			lpc.setPulsewidthC(int(data))	
		elif key == 'p':
			data = input(': Enter Camera Trigger to Laser Pulse Phase Offest (Usec) => ')
			lpc.setClockAtoBdelay(int(data))
		elif key == 'u':
			data = input(': Enter Camera Trigger to Auxillary Phase Offest (Usec) => ')
			lpc.setClockAtoCdelay(int(data))
		elif key == 'x':
			data = input(': Enter Auxillary Clock Modulus => ')
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
		elif key == 'm':
			print('')
			showMenu()
		else:
			print('')
			print('Not a memu item!')
		print('=> ',end='',flush=True)
			
			



