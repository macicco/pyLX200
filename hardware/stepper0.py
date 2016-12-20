#!/usr/bin/python

import math
import time,datetime
import pigpio

'''
Stepper class
Units:
	beta:steps
	betaTarget:steps
	v:steps/s
	a:steps/s**2

interface:

* move(steps,dir) -> move n steps relative to the current position
* goto(radians)   -> go to an absolute position in radians
* speed(rpm)      -> set speed
* 
'''

TIMESLOT=320000

class engine2steppers(object):
	def __init__(self,stepper0,stepper1):	
		self.pi=pigpio.pi('192.168.1.11')
		self.pi.wave_clear()
		self.s0=stepper0
		self.s1=stepper1
		self.old_wid=-9999

	def rpm(self,rpm0,rpm1):
		self.s0.setRPM(rpm0)
		self.s1.setRPM(rpm1)

	def move(self,steps0,steps1):
	   while not self.s0.syncronized or not self.s1.syncronized :
		self.s0.waveChunk()
		self.s1.waveChunk()
		self.sendWave()

	def sendWave(self):
		while ra.pi.wave_tx_busy(): 
			time.sleep(0.0001)

		wid = self.pi.wave_create() 
		self.pi.wave_send_once(wid)

		if self.old_wid !=-9999:
			print "DEL:",self.pi.wave_delete(self.old_wid)

		self.old_wid=wid

	def checkWaveBuffer(self):
		maxCBS=self.pi.wave_get_max_cbs()
		maxPulse=self.pi.wave_get_max_pulses()
		maxMicros=self.pi.wave_get_max_micros()
		print "MAX:",maxCBS,maxPulse,maxMicros
		
		CBS=self.pi.wave_get_cbs()
		Pulse=self.pi.wave_get_pulses()
		Micros=self.pi.wave_get_micros()
		print "ACTUAL:",CBS,Pulse,Micros	


	def clearWave(self):	
		self.pi.wave_clear()
	

class stepper(object):
	def __init__(self,name,stepsPerTurn,STEP_PIN,DIR_PIN,ENABLE_PIN,FAULT_PIN):
		self.pi=pigpio.pi('192.168.1.11')
		self.setPINs(STEP_PIN,DIR_PIN,ENABLE_PIN,FAULT_PIN)
		cb1 = self.pi.callback(self.STEP_PIN, pigpio.RISING_EDGE, self.stepCounter)
		cb2 = self.pi.callback(self.FAULT_PIN, pigpio.RISING_EDGE, self.fault)
		self.stepsPerTurn=stepsPerTurn
		self.microsteps=16
		self.name=name
		self.dir=1
		self.beta=0
		self.betaR=0
		self.betaTarget=0
		self.rpm=0
		self.freq=0
		self.syncronized=False

	def setPINs(self,STEP_PIN,DIR_PIN,ENABLE_PIN,FAULT_PIN):
		self.STEP_PIN=STEP_PIN
		self.DIR_PIN=DIR_PIN
		self.ENABLE=ENABLE_PIN
		self.FAULT_PIN=FAULT_PIN

		pi=self.pi
		pi.set_mode(self.STEP_PIN, pigpio.OUTPUT)
		pi.set_mode(self.DIR_PIN, pigpio.OUTPUT)
		pi.set_mode(self.ENABLE, pigpio.OUTPUT)
		pi.write(self.ENABLE,False)	

		pi.set_mode(self.FAULT_PIN, pigpio.INPUT)

	def setRPM(self,rpm):
		self.rpm=rpm
		self.freq=rpm*self.microsteps*self.stepsPerTurn/60

	def move(self,steps):
		self.betaTarget=self.betaTarget+steps


	def stepCounter(self,gpio, level, tick):
		dir=self.pi.read(self.DIR_PIN)
		if dir==1:
			dir=1
		else:
			dir=-1
		self.betaR=self.betaR+1*dir

	def fault(self):
		print "fault"


	def auxPINs(self,RESET_PIN,SLEEP_PIN,M0_PIN,M1_PIN,M2_PIN):
		pi=self.pi
		pi.set_mode(M2_PIN, pigpio.OUTPUT)
		pi.set_mode(M1_PIN, pigpio.OUTPUT)
		pi.set_mode(M0_PIN, pigpio.OUTPUT)
		pi.write(M2_PIN, True)
		pi.write(M1_PIN, False)
		pi.write(M0_PIN,False)

		pi.set_mode(RESET_PIN, pigpio.OUTPUT)
		pi.set_mode(SLEEP_PIN, pigpio.OUTPUT)
		pi.write(RESET_PIN, True)
		pi.write(SLEEP_PIN, True)




	def waveChunk(self):
		dir=self.dir
		lasting=TIMESLOT
		if self.freq!=0:
	 		t=500000/self.freq   #time in micros
			steps=int(self.freq*lasting/1000000.)
		else:
			steps=0
			return self.beta

		print lasting,steps,self.freq
		wave=[]
		for i in range(steps):
			wave.append(pigpio.pulse(0, 1<<self.STEP_PIN, t))
			wave.append(pigpio.pulse(1<<self.STEP_PIN, 0, t))
		self.pi.wave_add_generic(wave)
		dirwave=[]
		if dir>0:
			dirwave.append(pigpio.pulse(0,1<<self.DIR_PIN,t/2))
			dirwave.append(pigpio.pulse(1<<self.DIR_PIN,0,lasting-t/2))
			print "Forward"
		else:
			dirwave.append(pigpio.pulse(0,1<<self.DIR_PIN,t/2))
			dirwave.append(pigpio.pulse(0,1<<self.DIR_PIN,lasting-t/2))
			print "Backward"
		pulses=self.pi.wave_add_generic(dirwave)
		#self.checkWaveBuffer()
		print "Wave chunck lasting/cbs:",t*2.*steps/1000000,pulses
		self.beta=self.beta+steps*dir
		return self.beta
		




if __name__ == '__main__':
	ra=stepper("RA",200,13,5,21,4)
	ra.auxPINs(12,6,20,19,16)
	dec=stepper("DEC",48,18,22,8,17)
	dec.auxPINs(25,24,11,9,10,)
	e=engine2steppers(ra,dec)
	e.rpm(1,60)
	e.move(1,1)		
'''
'''





