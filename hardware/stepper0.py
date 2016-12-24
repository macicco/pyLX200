#!/usr/bin/python

import math
import time,datetime
import pigpio

'''
Stepper classes. It use the 'wave' funtionality include in 
pigpio library to send pulses to a drv8825 driver. Tested with
the hardware show in the "connections.png" file.

pigpio only has one DMA channel dedicate to wave. Thus we need
to compose all waves for all motos prior to send them throught
DMA channel. It is done in chuncks of pulses. As side effect is 
not posible to driver a single motor without command the others. 
For the same reason motor are perfectly syncronice each other.



interface:

* addStepper(stepperInstance) ->add a new motor to the engine.
* move(steps_list) 	-> move n steps relative to the current position
* rotate(degrees_list) 	-> go to an absolute position in degrees
* rmp(rpm0_list)       	-> set speed

In this context *_list are used to pass arguments because  we don't know 
how many steppers are in the engine at programing time.

* 
'''

TIMESLOT=100000
raspberry='192.168.1.11'

class engine(object):
	def __init__(self):	
		self.pi=pigpio.pi(raspberry)
		self.pi.wave_clear()
		self.steppers=[]
		self.old_wid=-9999

	def addStepper(self,stepper):
		self.steppers.append(stepper)
		print "Added new stepper #",len(self.steppers),stepper.name

	def rpm(self,rpm_list):
		for i,rpm,in enumerate(rpm_list):
			self.steppers[i].setRPM(rpm)

	def move(self,steps_list):
		for i,steps,in enumerate(steps_list):
			self.steppers[i].move(steps)
	   	self._move()
	
	def rotate(self,degrees_list):
		for i,degrees,in enumerate(degrees_list):
			self.steppers[i].rotate(degrees)
	   	self._move()

	def _move(self):
	   while not self._areSyncronized():
		for i,stepper,in enumerate(self.steppers):
			stepper.waveChunk()
		self._sendWave()

	def _sendWave(self):
		while ra.pi.wave_tx_busy(): 
			time.sleep(0.0001)

		wid = self.pi.wave_create() 
		self.pi.wave_send_once(wid)

		if self.old_wid !=-9999:
			self.pi.wave_delete(self.old_wid)

		self.old_wid=wid

	def _areSyncronized(self):
		answer=True
		for i,stepper,in enumerate(self.steppers):
			answer=answer and stepper.syncronized
		return answer
		
	def checkWaveBuffer(self):
		maxCBS=self.pi.wave_get_max_cbs()
		maxPulse=self.pi.wave_get_max_pulses()
		maxMicros=self.pi.wave_get_max_micros()
	
		CBS=self.pi.wave_get_cbs()
		Pulse=self.pi.wave_get_pulses()
		Micros=self.pi.wave_get_micros()
		print "CBS Pulses, Micros (ACTUAL/MAX)",CBS,maxCBS,Pulse,maxPulse,Micros,maxMicros


	def clearWave(self):	
		self.pi.wave_clear()



class stepper(object):
	def __init__(self,name,stepsPerTurn,STEP_PIN,DIR_PIN,ENABLE_PIN,FAULT_PIN):
		self.pi=pigpio.pi(raspberry)
		self.setPINs(STEP_PIN,DIR_PIN,ENABLE_PIN,FAULT_PIN)
		cb1 = self.pi.callback(self.STEP_PIN, pigpio.RISING_EDGE, self.stepCounter)
		cb2 = self.pi.callback(self.FAULT_PIN, pigpio.EITHER_EDGE, self.fault)
		self.stepsPerTurn=stepsPerTurn
		self.microsteps=16
		self.name=name
		self.dir=1
		self.beta=0
		self.betaR=0
		self.betaTarget=0
		self.rpm=0
		self.freq=0
		self.steps_rest=0
		self.syncronized=False
		self.old_time=time.time()

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
		self.freq=rpm*self.microsteps*self.stepsPerTurn/60.

	def move(self,steps):
	   	self.syncronized=False
		self.betaTarget=self.beta+steps
		#print self.name,"MOVE STEPS:",steps

	def rotate(self,degrees):
	   	self.syncronized=False
		target=degrees*(self.stepsPerTurn/360.)*self.microsteps
		#print target,self.betaTarget,self.beta
		self.betaTarget=target

	def stepCounter(self,gpio, level, tick):
		dir=self.pi.read(self.DIR_PIN)
		if dir==1:
			dir=1
		else:
			dir=-1
		self.betaR=self.betaR+1*dir
		#print self.betaR

	def fault(self,gpio, level, tick):
		if level==1:
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
		wave=[]
		lasting=TIMESLOT
		tmin=1
		delta=self.betaTarget-self.beta

		if delta*self.dir<0:
			newtime=time.time()
			print self.name,"DIR change",newtime-self.old_time
			self.old_time=newtime
			dir_change=True
			self.steps_rest=-self.steps_rest
			self.dir=self.dir*-1
		else:
			dir_change=False



		dir=self.dir
		if delta==0 or self.freq==0:
			steps=0
			if delta==0:
				self.syncronized=True
				#print self.name,"Syncronize"
			wave.append(pigpio.pulse(0, 1<<self.STEP_PIN, tmin))
			self.pi.wave_add_generic(wave)
			return 	self.beta
	

		steps_float=self.freq*lasting/1000000.
		steps=int(steps_float)
		self.steps_rest=self.steps_rest+(steps_float-steps)
		#print self.name,steps_float,steps,self.steps_rest
		if steps==0 and self.steps_rest<1:
			wave.append(pigpio.pulse(0, 1<<self.STEP_PIN, tmin))
			self.pi.wave_add_generic(wave)
			return 	self.beta


		if self.steps_rest>=1:
			print "STEP REST",int(self.steps_rest),self.steps_rest
			steps=steps+int(self.steps_rest)
			self.steps_rest=self.steps_rest-int(self.steps_rest)

		t=0.5*lasting/steps   #time in micros

		if abs(delta)<steps:
			pass
			#print "Delta",self.name,steps,delta,self.betaTarget,self.beta
			steps=int(abs(delta))






		for i in range(steps):
			wave.append(pigpio.pulse(0, 1<<self.STEP_PIN, t))
			wave.append(pigpio.pulse(1<<self.STEP_PIN, 0, t))
		self.pi.wave_add_generic(wave)

		if dir_change:
			dirwave=[]
			dirwave.append(pigpio.pulse(0,1<<self.DIR_PIN,t/2))
			if dir>0:
				pass
				#dirwave.append(pigpio.pulse(1<<self.DIR_PIN,0,lasting-t/2))
				dirwave.append(pigpio.pulse(1<<self.DIR_PIN,0,t/2))
			else:
				pass
				#dirwave.append(pigpio.pulse(0,1<<self.DIR_PIN,lasting-t/2))
				dirwave.append(pigpio.pulse(0,1<<self.DIR_PIN,t/2))
			pulses=self.pi.wave_add_generic(dirwave)
		#self.checkWaveBuffer()
		#print "Wave chunck lasting/cbs:",t*2.*steps/1000000,pulses
		self.beta=self.beta+steps*dir
		return self.beta
		




if __name__ == '__main__':
	e=engine()
	ra=stepper("RA",200,13,5,21,4)
	ra.auxPINs(12,6,20,19,16)
	dec=stepper("DEC",48,18,22,8,17)
	dec.auxPINs(25,24,11,9,10,)
	e.addStepper(ra)
	e.addStepper(dec)
	e.rpm((300,300))
	d=1
	while True:
		q0=int(200*16*360/(360.))
		q1=int(48*16*5/(360.))
		e.move((d*q0,d*q1))
		#time.sleep(0.1)
		d=d*-1
	e.rpm((300,200))		
	e.move((200*16*50,48*16*5))
	print "======================="
	e.rpm((60*1,60*1))
	e.move((-200*16*5,-48*16*5))				
	print "======================="
	e.rpm((0.1,1))
	e.move((200*16,48*16))
'''
'''





