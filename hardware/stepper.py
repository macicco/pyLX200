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
'''

TIMESLOT=1000000 # in microseconds


class wavePI(object):
	def __init__(self):
		self.pi=pigpio.pi('192.168.1.11')
		WAVES=3
		self.steppers=[]
		self.wid=[0]*WAVES
		self.currentWave=0

	def registerStepper(self,stepper):
		self.steppers.append(stepper)

	def loadWaves(self):
		self.pi.wave_add_generic(wave)

	def sendNextWave(self):
		wid[self.currentWave] = self.pi.wave_create() 
		print self.pi.wave_send_using_mode(wid[self.currentWave],pigpio.WAVE_MODE_ONE_SHOT_SYNC)
		self.currentWave+=1
		if self.currentWave>WAVES:
			self.currentWave=0

	def checkWaveBuffer(self):
		maxCBS=self.pi.wave_get_max_cbs()
		maxPulse=self.pi.wave_get_max_pulses()
		maxMicros=self.pi.wave_get_max_micros()
		print "MAX:",maxCBS,maxPulse,maxMicros
		
		CBS=self.pi.wave_get_cbs()
		Pulse=self.pi.wave_get_pulses()
		Micros=self.pi.wave_get_micros()
		print "ACTUAL:",CBS,Pulse,Micros	


	def clearWaves(self):	
		self.pi.wave_clear()

class stepper(object):
	def __init__(self,name,STEP_PIN,DIR_PIN,ENABLE_PIN):
		self.pi=pigpio.pi('192.168.1.11')
		self.setPINs(STEP_PIN,DIR_PIN,ENABLE_PIN)
		cb1 = self.pi.callback(self.STEP_PIN, pigpio.RISING_EDGE, self.stepCounter)
		self.name=name
		self.dir=1
		self.beta=0
		self.betaTarget=0
		self.v=0
		self.a=0
		self.waveChunks=[]


	def setPINs(self,STEP_PIN,DIR_PIN,ENABLE_PIN):
		self.STEP_PIN=STEP_PIN
		self.DIR_PIN=DIR_PIN
		self.ENABLE=ENABLE_PIN

		pi=self.pi
		pi.set_mode(self.STEP_PIN, pigpio.OUTPUT)
		pi.set_mode(self.DIR_PIN, pigpio.OUTPUT)
		pi.set_mode(self.ENABLE, pigpio.OUTPUT)
		pi.write(self.ENABLE,False)

	def auxPINs(self,RESET_PIN,SLEEP_PIN,M0_PIN,M1_PIN,M2_PIN):
		pi=self.pi
		pi.set_mode(M2_PIN, pigpio.OUTPUT)
		pi.set_mode(M1_PIN, pigpio.OUTPUT)
		pi.set_mode(M0_PIN, pigpio.OUTPUT)
		pi.write(M2_PIN, False)
		pi.write(M1_PIN, False)
		pi.write(M0_PIN,False)

		pi.set_mode(RESET_PIN, pigpio.OUTPUT)
		pi.set_mode(SLEEP_PIN, pigpio.OUTPUT)
		pi.write(RESET_PIN, True)
		pi.write(SLEEP_PIN, True)

	def setRPM(self,rpm):
		self.rpm=rpm


	def stepCounter(self,gpio, level, tick):
		dir=self.pi.read(self.DIR_PIN)
		if dir==1:
			dir=1
		else:
			dir=-1
		self.beta=self.beta+1*dir

	def waveChunk(self,freq,steps,dir):
		t=500000/freq   #time in micros
		lasting=steps*2*t
		print lasting
		wave=[]
		for i in range(steps):
			wave.append(pigpio.pulse(0, 1<<self.STEP_PIN, t))
			wave.append(pigpio.pulse(1<<self.STEP_PIN, 0, t))
		self.waveChunks.append(wave)
		dirwave=[]
		if dir>0:
			dirwave.append(pigpio.pulse(0,1<<self.DIR_PIN,t/2))
			dirwave.append(pigpio.pulse(1<<self.DIR_PIN,0,lasting-t/2))
		else:
			dirwave.append(pigpio.pulse(0,1<<self.DIR_PIN,t/2))
			dirwave.append(pigpio.pulse(0,1<<self.DIR_PIN,lasting-t/2))

		self.waveChunks.append(dirwave)
		print 	len(self.waveChunks)






if __name__ == '__main__':

	waver=wavePI()
	waver.clearWaves()

	ra=stepper("RA",13,5,21)
	ra.auxPINs(12,6,20,19,16)
	waver.registerStepper(ra)

	ra.waveChunk(100,100,1)
	ra.waveChunk(850,100,1)

	'''
	dec=stepper("DEC",18,22,8)
	dec.auxPINs(25,24,11,9,10)
	dec.waveChunk(30,64,1)
	dec.waveChunk(20,64,1)
	'''

'''
'''





