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

	def run(self):
		while  self.RUN:
			pass

	def setPINs(self,STEP_PIN,DIR_PIN,ENABLE_PIN):
		self.STEP_PIN=STEP_PIN
		self.DIR_PIN=DIR_PIN
		self.ENABLE=ENABLE_PIN

		pi=self.pi
		pi.set_mode(self.STEP_PIN, pigpio.OUTPUT)
		pi.set_mode(self.DIR_PIN, pigpio.OUTPUT)
		pi.set_mode(self.ENABLE, pigpio.OUTPUT)
		pi.write(self.ENABLE,False)

	


	def setRPM(self,rpm):
		self.rpm=rpm


	def stepCounter(self,gpio, level, tick):
		dir=self.pi.read(self.DIR_PIN)
		if dir==1:
			dir=1
		else:
			dir=-1
		self.beta=self.beta+1*dir


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


	def waveChunk(self,freq,steps,dir):
		t=500000/freq   #time in micros
		lasting=steps*2*t
		print lasting
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

	def sendWave(self):
		wid = self.pi.wave_create() 
		print self.pi.wave_send_using_mode(wid,pigpio.WAVE_MODE_ONE_SHOT_SYNC)
		#print self.pi.wave_send_once(wid)

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


if __name__ == '__main__':
	ra=stepper("RA",13,5,21)
	ra.auxPINs(12,6,20,19,16)
	ra.clearWave()


	ra.waveChunk(20,100,1)
	ra.waveChunk(10,100,-1)

	dec=stepper("DEC",18,22,8)
	dec.auxPINs(25,24,11,9,10)
	dec.waveChunk(20,64,1)
	dec.waveChunk(10,64,1)

	ra.sendWave()
'''
'''





