# Python class to DHM (Digital Holographic Microscope) Laser Controller
import time
import sys
import serial
import serial.tools.list_ports as ports

# Class for DHM Laser Controller
# for python 3
class laserPulseController:
	def __init__(self):
		self.serial = serial.Serial()
		self.serial.portBaudrate  = 9600
		self.serial.timeout = 0.5
		self.verbose = 1
		self.line = ''
		self.lineIn = 0
		self.currentFrequency    = 0.0
		self.currentPulsewidthA  = 0
		self.currentProbabilityA = 0
		self.currentPulsewidthB  = 0
		self.currentProbabilityB = 0
		self.currentModulusB     = 0
		self.currentPulsewidthC  = 0
		self.currentModulusC     = 0
		self.currentAtoBdelay    = 0
		self.currentAtoCdelay    = 0
		self.currentRunState     = 0
		self.currentCountdown	 = 0
		self.currentCountdownState = 0
		self.currentExternalInterruptState = 0
		self.currentInterruptSense = 0
		
		self.port_found = False
		self.serial.port = 'NONE'
		lpi = ports.comports()
		# Iterate over the com list to find first Arduino port
		for x in lpi[:]:
			print(x.description)
			ArduinoText = ''
			if sys.platform == 'win32':
			    ArduinoText = 'Arduino Due Programming Port'
			else:
			    ArduinoText = 'Arduino Due Prog. Port'

			if x.description.find(ArduinoText) >= 0:
				self.serial.port = x.device
				self.port_found = True
				break;
		
	def open(self):
		if(self.port_found):
			self.serial.open();
			time.sleep(.1) # Wait for banner to start transmitting
			self.readLine() # The banner itself
			banner = self.line
			self.readLine() # The ready message
			self.readLine() # The empty cr/lf	
			if self.verbose: print(banner)
			self.disableCommandAcknowledge();
		else: print('Sorry, No Laser Pulse Controller Port Found');
		
	
	def readLine(self):
		i = 0
		self.lineIn = 0
		self.line = ''
		# print i
		while i < 100 and self.lineIn == 0:
			# print i
			if self.serial.in_waiting:
				ch = self.serial.read(1)
				ch = ch.decode('ASCII')
				# print(ch)
				self.line = self.line + ch
				if ch == '\n':
					self.lineIn = 1
					self.line = self.line[:len(self.line)-2]	
			else:
				i += 1;
				time.sleep(0.01)
		
	def close(self):
		self.serial.close()
		
	def flushInputBuffer(self):
		self.serial.reset_input_buffer();
		
	def flushOutputBuffer(self):
		self.serial.reset_output_buffer();
	
	def startClocks(self):
		cmd = b'start' + b'\r\n'
		self.serial.write(cmd)
		
	def stopClocks(self):
		cmd = b'stop' + b'\r\n'
		self.serial.write(cmd)
		
	def setExternalInterruptSense(self,pol):
		if(pol == True):
			cmd = b'trigger_interrupt_sense 1' + b'\r\n'
		else:
			cmd = b'trigger_interrupt_sense 0' + b'\r\n'
		self.serial.write(cmd)
		
	def enableClocksCountdown(self):
		cmd = b'enable clocks_countdown' + b'\r\n'
		self.serial.write(cmd)
		
	def enableCommandAcknowledge(self):
		cmd = b'enable command_acknowledge' + b'\r\n'
		self.serial.write(cmd)
		
	def enableExternalTrigger(self):
		cmd = b'enable external_trigger' + b'\r\n'
		self.serial.write(cmd)
		
	def disableClocksCountdown(self):
		cmd = b'disable clocks_countdown' + b'\r\n'
		self.serial.write(cmd)
		
	def disableCommandAcknowledge(self):
		cmd = b'disable command_acknowledge' + b'\r\n'
		self.serial.write(cmd)
		
	def disableExternalTrigger(self):
		cmd = b'disable external_trigger' + b'\r\n'
		self.serial.write(cmd)
	
	def setClockA_Output(state):
		if state > 0: out = 'high'
		else: out = b'low'
		cmd = b'set clockA_output ' + out + b'\r\n'
		self.serial.write(cmd)
		
	def setClockB_Output(state):
		if state > 0: out = 'high'
		else: out = b'low'
		cmd = b'set clockB_output ' + out + b'\r\n'
		self.serial.write(cmd)
		
	def setClockC_Output(state):
		if state > 0: out = 'high'
		else: out = b'low'
		cmd = b'set clockC_output ' + out + b'\r\n'
		self.serial.write(cmd)
		
	def setFrequency(self,frequency):
		# Calculate the corresponding, rounded up period in microseconds
		period = int(round((1.0/frequency)*1000000.0))
		# Make command string
		cmd = b'set clocks_frequency ' + str(period).encode('ASCII') + b'\r\n'
		# send it
		self.serial.write(cmd)
		
	def setProbabilityA(self, probability):
		cmd = b'set clockA_probability ' + str(probability).encode('ASCII') + b'\r\n'
		self.serial.write(cmd)
		
	def setPulsewidthA(self, width):
		cmd = b'set clockA_pulsewidth ' + str(width).encode('ASCII') + b'\r\n'
		self.serial.write(cmd)
		
	def setProbabilityB(self, probability):
		cmd = b'set clockB_probability ' + str(probability).encode('ASCII') + b'\r\n'
		self.serial.write(cmd)
		
	def setPulsewidthB(self, width):
		cmd = b'set clockB_pulsewidth ' + str(width).encode('ASCII') + b'\r\n'
		self.serial.write(cmd)
		
	def setPulsewidthC(self, width):
		cmd = b'set clockC_pulsewidth ' + str(width).encode('ASCII') + b'\r\n'
		self.serial.write(cmd)
		
	def setModulusB(self, modulus):
		cmd = b'set clockB_modulus ' + str(modulus).encode('ASCII') + b'\r\n'
		self.serial.write(cmd)
		
	def setModulusC(self, modulus):
		cmd = b'set clockC_modulus ' + str(modulus).encode('ASCII') + b'\r\n'
		self.serial.write(cmd)	
		
	def setClockAtoBdelay(self, delay):
		cmd = b'set clockAtoB_delay ' + str(delay).encode('ASCII') + b'\r\n'
		self.serial.write(cmd)
		
	def setClockAtoCdelay(self, delay):
		cmd = b'set clockAtoC_delay ' + str(delay).encode('ASCII') + b'\r\n'
		self.serial.write(cmd)
		
	def setCountdown(self, countdown):
		cmd = b'set clocks_downcount ' + str(countdown).encode('ASCII') + b'\r\n'
		self.serial.write(cmd)
		
	def freeRun(self,frequency,pulsewidthA,pulsewidthB,AtoBdelay):
		self.disableClocksCountdown()
		self.disableExternalTrigger()
		self.setProbabilityA(1.0)
		self.setProbabilityB(1.0)
		self.setFrequency(frequency)
		self.setPulsewidthA(pulsewidthA)
		self.setPulsewidthB(pulsewidthB)
		self.setClockAtoBdelay(AtoBdelay)
		self.startClocks()
		
	def updateCurrentSettings(self):
		cmd = b'get current_settings\r\n'
		self.serial.write(cmd)
		self.readLine() # Get period in us
		period = float(self.line)/1000000.0 # Period in seconds
		self.currentFrequency = (1.0/period)
		self.readLine()
		self.currentPulsewidthA = int(self.line)
		self.readLine()
		self.currentProbabilityA = int(self.line)
		self.readLine()
		self.currentPulsewidthB = int(self.line)
		self.readLine()
		self.currentProbabilityB = int(self.line)
		self.readLine()
		self.currentPulsewidthC = int(self.line)
		self.readLine()
		self.currentModulusC = int(self.line)
		self.readLine()
		self.currentAtoBdelay = int(self.line)
		self.readLine()
		self.currentAtoCdelay = int(self.line)
		self.readLine()
		self.currentRunState = int(self.line)
		self.readLine()
		self.currentModulusB = int(self.line)
		self.readLine()
		self.currentCountdown = int(self.line)
		self.readLine()
		self.currentCountdownState = int(self.line)
		self.readLine()
		self.currentExternalInterruptState = int(self.line)
		self.readLine()
		self.currentInterruptSense = int(self.line)
		
	
	
		
	
	
	
	


			

		
	
