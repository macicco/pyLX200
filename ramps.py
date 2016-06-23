#!/usr/bin/python

import math
import time,datetime
from config import *
import ephem





#virtual class. It must be used to derive the actual driver class
#which implemente the motor driver
class axis(object):
	def __init__(self,name):
		self.log=True
		self.setName(name)
		self.pointError=ephem.degrees(0)
		self.timestepMax=0
		self.timestepMin=0
		self.timestep=self.timestepMax
		self.acceleration=ephem.degrees(engine['acceleration'])
		self.a=ephem.degrees(0)
		self.v=ephem.degrees(0)
		self.vmax=ephem.degrees(ephem.degrees('05:00:00'))
		self.beta=ephem.degrees(0)
		self.beta_target=ephem.degrees(0)
		self.t2target=0
		self._vmax=self.v
		self.vtracking=0
		self.slewend=False
		self.RUN=True
		self.T0=time.time()


	def setName(self,name):
		self.name=name
		if self.log:
			self.logfile=open(str(self.name)+".log",'w')
			line="T timestep timesleep vmax beta_target beta v a motorBeta steps\r\n"
			self.logfile.write(line)



	def slew(self,beta,blocking=False):

		self.slewend=False
		self.beta_target=ephem.degrees(beta)
		if not blocking:
			return
	        while not self.slewend:
			time.sleep(1)

	def track(self,v):
		#not needed now. If not slewing is tracking
		return
		#print "TRACKING START"
		self.vtracking=ephem.degrees(v)



	def sync(self,b):
		self.beta_target=ephem.degrees(b)
		self.beta=ephem.degrees(b)


	#Main loop thread
	@threaded
	def run(self):
		self.T=time.time()
		while  self.RUN:
			#estimate the timestep based on the error point
			if self.v !=0:
				self.timesleep=abs(float(self.pointError)/(self.v))
				if self.timesleep<self.timestepMin:
					self.timesleep=self.timestepMin
				if self.timesleep>self.timestepMax:
					self.timesleep=self.timestepMax
			else:
				self.timesleep=self.timestepMax

			#now calculate the actual timestep
			now=time.time()
			deltaT=now-self.T

			#print self.name,self.timestep,deltaT,self.v
			self.timestep=deltaT
			if self.slewend:
				steps=self.tracktick()
			else:
				steps=self.slewtick()
			
			self.doSteps(steps)
			self.T=now
			time.sleep(self.timesleep)
		print "rampsThread ended"

	def tracktick(self):
		steps=self.vtracking*self.timestep
		self.beta=self.beta+steps
		self.beta_target=self.beta
		self.v=self.vtracking
		return steps

	#NOT IN USE. 
	#Change speed smoothly 
	def tracktickSmooth(self):
		self.vdelta=self.vtracking-self.v
		sign=math.copysign(1,self.vdelta)
		self.beta_slope=(self.v*self.v)/(2*self.acceleration) 
		self.t_slope=self.v/self.acceleration  
		self.a=self.acceleration*sign
		self.v=self.v+self.a*self.timestep

	   	#check if already at max speed
		if abs(self.v-self.vtracking) <=0.01:
			self.v=self.vtracking
			self.a=0

		steps=self.v*self.timestep+self.a*(self.timestep*self.timestep)/2
		self.beta=self.beta+steps
		#print self.beta,self.v,self.a,steps

		return steps

	def slewtick(self):
		if self.slewend:
			#This change to tracktick() in run()		
			steps=0
			return steps

		#Update target position with the tracking speed
		self.beta_target=self.beta_target+self.vtracking*self.timestep

		self.delta=self.beta_target-self.beta
		sign=math.copysign(1,self.delta)
		v_sign=math.copysign(1,self.v)

		self.beta_slope=(self.v*self.v)/(2*self.acceleration) 
		self.t_slope=self.v/self.acceleration  

		#check if arrived to target	
		#if  abs(self.delta) <= self.pointError and abs(self.v)<=self.pointError:
		if  abs(self.delta) <= self.pointError:
			self.slewend=True
			self.v=self.vtracking
			self.a=0
			steps=self.delta
			self.beta=self.beta+steps
			self.track(self.vtracking)
			#self.beta=ephem.degrees(self.beta_target)
			print self.name,"Slew End",ephem.degrees(self.beta)
			return steps


		#check if it is time to deccelerate
		if abs(self.delta) - self.beta_slope<=0 :
			self.a=-self.acceleration*sign
			#print self.name,"Decelerating:",self.a
		else:
			if abs(self.v)<abs(self._vmax):
				self.a=self.acceleration*sign

		#Change in direction
		if sign!=v_sign:
			self.a=self.acceleration*sign

	   	#check if already at max speed
		if abs(self.v)>abs(self._vmax):
			if sign==v_sign:
				self.v=self._vmax*v_sign
				self.a=0
			
		self.v=ephem.degrees(self.v+self.a*self.timestep)
		steps=self.v*self.timestep+self.a*(self.timestep*self.timestep)/2
		self.beta=self.beta+steps
		return steps

	def doSteps(self,steps):
		#sleep
		time.sleep(self.timesleep)
		if self.log:
			self.saveDebug(steps,0)
		
	def saveDebug(self,steps,motorBeta):
		line="%g %g %g %g %g %g %g %g %g %g\r\n" % (time.time()-self.T0,self.timestep, \
			self.timesleep,self._vmax,self.beta_target,self.beta,self.v,self.a,motorBeta,steps)
		self.logfile.write(line)

#Stepper raspberry implementation
class AxisDriver(axis):
	def __init__(self,name,PIN,DIR_PIN):
		super(AxisDriver, self).__init__(name)
		self.lock = threading.Lock()
		import pigpio
		self.pi=pigpio.pi(servers['pigpio'])
		self.PIN=PIN
		self.DIR_PIN=DIR_PIN
		self.stepsPerRevolution=gear['motorStepsRevolution']*gear['microstep']*gear['reducer']
		self.corona=gear['corona']
		self.plate=gear['pinion']
		self.FullTurnSteps=self.plate*self.stepsPerRevolution/self.corona
		self.stepsRest=0
		self.maxPPS=engine['maxPPS']
		self.pulseWidth=1./float(self.maxPPS)
		self.timestepMax=self.pulseWidth*10
		self.timestepMin=self.pulseWidth*5
		self.timestep=self.timestepMax
		self.pulseDuty=0.5
		self.minMotorStep=math.pi*2/float(self.FullTurnSteps)
		self.vmax=self.minMotorStep/self.pulseWidth
		self._vmax=self.vmax
		self.pointError=self.minMotorStep
		self.stepTarget=0
		self.motorBeta=0
		self.dire=1
		self.pi.write(self.DIR_PIN, self.dire>0)
		self.freq=0
		self.updatePWM=False
		self.deltavFine=0
		self.PWMwatchdog=0
		self.pi.set_mode(self.PIN, pigpio.OUTPUT)
		self.pi.set_mode(self.DIR_PIN, pigpio.OUTPUT)
		self.pi.hardware_PWM(self.PIN,10,0)
		cb1 = self.pi.callback(self.PIN, pigpio.RISING_EDGE, self.stepCounter)
		cb2 = self.pi.callback(self.PIN, pigpio.FALLING_EDGE, self.falling)

		print "StepsPerRev",self.stepsPerRevolution \
			,"FullTurnSteps: ",self.FullTurnSteps \
			,"PPS",1/self.pulseWidth,"Phisical:",self.minMotorStep
		print "Min step (point Error)",ephem.degrees(self.minMotorStep) \
			,"Max speed: ",ephem.degrees(self._vmax)



	def doSteps(self,delta):
		#Distribute steps on 
		#delta is in radians. Calculate actual steps 
		steps=delta/self.minMotorStep+self.stepsRest
		Isteps=round(steps)


		#acumultate the fractional part to the next step
		self.stepsRest=steps-Isteps

		if self.log:
			motorBeta=float(self.motorBeta)*self.minMotorStep
			self.saveDebug(self.stepTarget-self.motorBeta,motorBeta)
			#self.saveDebug(self.deltavFine,motorBeta)
			#self.saveDebug(self.stepTarget,motorBeta)

		#calculate direction of motion
		'''Now is done in setPWMSpeed() '''


		#calculate target steps
	   	self.stepTarget=self.stepTarget+Isteps

		self.deltavFine=ephem.degrees(self.beta-self.motorBeta*self.minMotorStep)
		self.setPWMspeed(self.v+self.deltavFine)
		#self.setPWMspeed(self.v)

		'''
		if self.v==0:
			self.extraSteps()'''

	#NOT IN USE. 
	#do extra steeps to get stepTarget 
	def extraSteps(self):
		deltaSteps=self.beta/self.minMotorStep
		deltaFine=int(deltaSteps-self.motorBeta)
		if abs(deltaFine)>=1:
			d=math.copysign(1,deltaFine)
			self.pi.write(self.DIR_PIN, d>0)
			print deltaFine
			self.pi.hardware_PWM(self.PIN,0,self.pulseDuty*1000000)
			for i in range(0,abs(deltaFine)):
				self.pi.write(self.PIN, 1)
				time.sleep(self.pulseWidth)
				self.pi.write(self.PIN, 0)
				time.sleep(self.pulseWidth)
			self.pi.hardware_PWM(self.PIN,self.freq,self.pulseDuty*1000000)


	def setPWMspeed(self,v):
		with self.lock:
			freq=0
			#calculate direction of motion
			if self.dire*v<0:
				self.dire=math.copysign(1,v)
				self.pi.write(self.DIR_PIN, self.dire>0)

			freq=round(abs(v)/self.minMotorStep)
			if freq  >=self.maxPPS:
				freq=self.maxPPS

			#PWM freq change on falling edge so we need to start if stopped
			PWMstopped=(self.pi.get_PWM_dutycycle(self.PIN) == 0)
			if (PWMstopped or freq<10) and freq!=0:
				self.freq=freq
				self.pi.hardware_PWM(self.PIN,self.freq,self.pulseDuty*1000000)
				'''if self.freq!=0:
					self.pi.hardware_PWM(self.PIN,self.freq,self.pulseDuty*1000000)
				else:
					self.pi.hardware_PWM(self.PIN,10,0)'''
			   	self.updatePWM=False
			else:
				self.freq=freq
			   	self.updatePWM=True
			self.PWMwatchdog+=1
		return self.freq



	def falling(self,gpio, level, tick):
		with self.lock:
			if self.updatePWM==True:
				if self.freq!=0:
					self.pi.hardware_PWM(self.PIN,self.freq,self.pulseDuty*1000000)
				else:
					self.pi.hardware_PWM(self.PIN,10,0)
				self.updatePWM==False

	def stepCounter(self,gpio, level, tick):
	    #avoid to put locks here. Danger of miss steps!
     	    #with self.lock:
		self.PWMwatchdog=0
		dire=self.pi.read(self.DIR_PIN)
		if dire==1:
			dire=1
		else:
			dire=-1
		self.motorBeta=self.motorBeta+1*dire


class mount:
	def __init__(self):
		simulation=False
		if simulation:
			self.axis1=axis('RA')
			self.axis2=axis('DEC')
		else:
			self.axis1=AxisDriver('RA',12,4)
			self.axis2=AxisDriver('DEC',13,5)


		self.run()

	def run(self):					
		self.axis1.run()
		self.axis2.run()

	def slew(self,x,y,blocking=False):
		self.setVmax(x,y)
		self.axis1.slew(x,blocking)
		self.axis2.slew(y,blocking)

	def sync(self,x,y):
		self.axis1.sync(x)
		self.axis2.sync(y)

	def slewend(self):
		return (self.axis1.slewend and self.axis2.slewend)

	def stopSlew(self):
		self.axis1.slew(self.axis1.beta)
		self.axis2.slew(self.axis2.beta)

	def track(self,vx,vy):
		self.axis1.track(vx)
		self.axis2.track(vy)

	def trackSpeed(self,vx,vy):
		self.axis1.vtracking=ephem.degrees(vx)
		self.axis2.vtracking=ephem.degrees(vy)

	def compose(self,x,y):
		deltax=x-self.axis1.beta
		deltay=y-self.axis2.beta
		angle=math.atan2(y, x)
		module=math.sqr(deltax*deltax+deltay*deltay)
		return module,angle
	
	def setVmax(self,x,y):
		deltax=abs(x-self.axis1.beta)
		deltay=abs(y-self.axis2.beta)
		self.axis1._vmax=float(self.axis1.vmax)
		self.axis2._vmax=float(self.axis2.vmax)
		return
		if deltax==0 or deltay==0:
			return		
		if deltax > deltay:
			self.axis2._vmax=self.axis2.vmax*deltay/deltax
		else:
			self.axis1._vmax=self.axis1.vmax*deltax/deltay
		#print "VAXIS:",self.axis1._vmax,self.axis2._vmax
		return

	def coords(self):
		print time.time()-self.T0,self.axis1.timestep,self.axis2.timestep,self.axis1.beta, \
			self.axis2.beta,self.axis1.v,self.axis2.v,self.axis1.a,self.axis2.a

	def end(self):
		self.axis1.RUN=False
		self.axis2.RUN=False





if __name__ == '__main__':
	m=mount()
	vRA=ephem.degrees('-00:00:15')
	m.trackSpeed(vRA,0)
	RA=ephem.hours('03:00:00')
	DEC=ephem.degrees('15:00:00')
	m.slew(RA,DEC)
	t=0
	while t<15:
		t=t+m.axis1.timestep
		time.sleep(m.axis1.timestep)
		#m.coords()
	RA=ephem.hours('01:00:00')
	DEC=ephem.degrees('-15:00:00')
	m.slew(RA,DEC)
	t=0
	while t<15:
		t=t+m.axis1.timestep
		time.sleep(m.axis1.timestep)
		#m.coords()
	m.end()

