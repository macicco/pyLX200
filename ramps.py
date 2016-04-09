#!/usr/bin/python

import math
import time,datetime
import threading
import ephem

raspi=True

if raspi:
	import pigpio
	pi=pigpio.pi('cronostamper')

#Decorator to run some functions in threads
def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

#virtual class. It must be used to derive driver class
#wich implemente the motor dirver
class axis(object):
	def __init__(self,a,v,pointError):
		self.debug=True
		self.name=0
		self.pointError=float(pointError)
		self.timestepMax=0.01
		self.timestepMin=0.001
		self.timestep=self.timestepMax
		self.acceleration=float(a)
		self.a=0
		self.vmax=float(v)
		self.beta=0
		self.v=0
		self.beta_target=0
		self.t2target=0
		self._vmax=v
		self.tracking=False
		self.vtracking=0
		self.slewend=False
		self.kill=False
		self.deltaOld=0
		self.T0=time.time()
		#self.say()

	def setName(self,name):
		self.name=name
		if self.debug:
			self.logfile=open(str(self.name)+".log",'w')
			line="T timestep timesleep vmax beta_target, beta v a steps\n"
			self.logfile.write(line)

	def say(self):
		print self.acceleration,self.vmax,self.v
		print self.t_slope,self.beta_slope
		print self.beta,self.beta_target,self.t2target
		print self._vmax



	def slew(self,beta,blocking=False):
		self.tracking=False
		#print "TRACKING END"
		#print "SLEW START"
		self.slewend=False
		self.beta_target=beta
		#self.v=self.vtracking
		if not blocking:
			return
	        while not self.slewend:
			time.sleep(1)

	def track(self,v):
		#print "TRACKING START"
		self.tracking=True
		self.vtracking=v



	def sync(self,b):
		self.beta_target=b
		self.beta=b


	@threaded
	def run(self):
		self.T=time.time()
		while not self.kill:
			#estimate the timestep based on the error point
			if self.v !=0:
				self.timesleep=abs(float(self.pointError)/(self.v*3))
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

			if self.tracking:
				steps=self.tracktick()
			else:
				steps=self.slewtick()
			
			self.doSteps(steps)
			self.T=now

	def tracktick(self):
		steps=self.vtracking*self.timestep
		self.beta=self.beta+steps
		self.v=self.vtracking
		return steps

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
		if abs(self.delta) - self.beta_slope<=0:
			self.a=-self.acceleration*sign
			#print self.name,"Decelerating:",self.a
		else:
			self.a=self.acceleration*sign


	   	#check if already at max speed
		if abs(self.v)>abs(self._vmax):
			if sign==v_sign:
				self.v=self._vmax*v_sign
				self.a=0
				print self.name,"V MAX :",ephem.degrees(self.v),ephem.degrees(self.v*self.timestep)

		self.v=self.v+self.a*self.timestep
		steps=self.v*self.timestep+self.a*(self.timestep*self.timestep)/2
		self.beta=self.beta+steps
		self.deltaOld=self.delta
		#print self.name,"V,v*timestep,steps",ephem.degrees(self.v),ephem.degrees(self.v*self.timestep),ephem.degrees(steps)
		return steps

	def doSteps(self,steps):
		#sleep
		time.sleep(self.timesleep)
		if self.debug:
			self.saveDebug(steps)
		
	def saveDebug(self,steps):
		line="%g %g %g %g %g %g %g %g %d\n" % (time.time()-self.T0,self.timestep,self.timesleep,self._vmax,self.beta_target,self.beta,self.v,self.a,steps)
		self.logfile.write(line)

#Stepper implementation
class AxisDriver(axis):
	def __init__(self,a,v,pointError,PIN):
		super(AxisDriver, self).__init__(a,v,pointError)
		self.PIN=PIN
		self.stepsPerRevolution=200*16*1 	#Motor:steps*microsteps*gearbox
		self.corona=30
		self.plate=500
		self.FullTurnSteps=self.plate*self.stepsPerRevolution/self.corona
		self.stepsRest=0
		self.pulseWidth=0.001    		#in seconds
		self.pulseDuty=0.5
		self.pointError=math.pi*2/self.FullTurnSteps
		self.vmax=self.pointError/self.pulseWidth
		self._vmax=self.vmax
		self.acceleration=self.vmax/10.
		print "Min step (point Error)",ephem.degrees(self.pointError) \
			,"Max speed: ",ephem.degrees(self._vmax)


	
	def doSteps(self,delta):
		#Distribute steps on 
		#delta is in radians. Calculate actual steps 
		steps=(self.FullTurnSteps*delta)/(math.pi*2)+self.stepsRest
		Isteps=round(steps)

		#acumultate the not integer part
		self.stepsRest=steps-Isteps

		#calculate direction of motion
		if Isteps<0:
			dire=-1
		else:
			dire=1

		Isteps=int(abs(Isteps))

		if Isteps==0:
			pulseLasting=0
			time.sleep(self.timesleep)
			return		
		else:
			pulseLasting=self.timesleep/float(Isteps)
			#print self.name,self.timestep-self.timesleep,Isteps,pulseLasting,Isteps*pulseLasting,self.timestep

		#print delta,self.timesleep,self.timestep
		#print self.timesleep,self.name,ephem.degrees(delta),dir,Isteps,self.stepsRest,pulseLasting,self.timesleep,self.timestep

		if self.debug:
			self.saveDebug(Isteps*dire)



		if pulseLasting-self.pulseWidth <0:
			print self.name,"\tTiming error (pulseLasting,pulseWidth,Isteps,timestep,timesleep)",\
                              pulseLasting,self.pulseWidth,Isteps,self.timestep,self.timesleep

		for p in range(Isteps):
		   if raspi:
			pi.write(self.PIN, 1)
			time.sleep(self.pulseWidth*self.pulseDuty)
			pi.write(self.PIN, 0)
			if pulseLasting-self.pulseWidth <0:
				#print self.name,"timestep: to low for pulsewidth. Timing error",pulseLasting,self.pulseWidth,p
				time.sleep(self.pulseWidth*(1.-self.pulseDuty))
				#time.sleep(self.pulseWidth*0.1)
				pass
			else:
				#print self.name," OK ",pulseLasting,self.pulseWidth
				time.sleep(pulseLasting-self.pulseWidth*self.pulseDuty)




class mount:
	def __init__(self,a,v,pointError):
		self.axis1=AxisDriver(a,v,pointError,4)
		self.axis2=AxisDriver(a,v,pointError,5)
		#self.axis1=axis(a,v,pointError)
		#self.axis2=axis(a,v,pointError)
		self.axis1.setName("RA")
		self.axis2.setName("DEC")
		self.T0=time.time()
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

	def stopSlew(self):
		self.axis1.slew(self.axis1.beta)
		self.axis2.slew(self.axis2.beta)

	def track(self,vx,vy):
		self.axis1.track(vx)
		self.axis2.track(vy)

	def trackSpeed(self,vx,vy):
		self.axis1.vtracking=vx
		self.axis2.vtracking=vy
		#print "TRACK SPEED",self.axis1.vtracking,self.axis2.vtracking

	def compose(self,x,y):
		deltax=x-self.axis1.beta
		deltay=y-self.axis2.beta
		angle=math.atan2(y, x)
		print deltax,deltay,angle
	
	def setVmax(self,x,y):
		deltax=abs(x-self.axis1.beta)
		deltay=abs(y-self.axis2.beta)
		self.axis1._vmax=float(self.axis1.vmax)
		self.axis2._vmax=float(self.axis2.vmax)
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
		self.axis1.kill=True
		self.axis2.kill=True


if __name__ == '__main__':
	#m=mount(1,1)
	a=ephem.degrees('01:00:00')
	v=ephem.degrees('05:00:00')
	e=ephem.degrees('00:00:01')
	m=mount(a,v,e)
	m.trackSpeed(e,0)
	RA=ephem.hours('01:00:00')
	DEC=ephem.degrees('-30:30:00')
	m.slew(RA,DEC)
	t=0
	while t<15:
		t=t+m.axis1.timestep*2
		time.sleep(m.axis1.timestep*2)
		#m.coords()
	m.end()
	exit(0)

	RA_axis=axis(1.,1.)
	RA_axis.run()
	for i,v in enumerate(xrange(0,600)):
		x=math.sin(float(v)/100.)
		RA_axis.track(x)
		time.sleep(RA_axis.timestep*2)
		#print RA_axis.beta,RA_axis.v,RA_axis.a,x
	RA_axis.kill=True

	'''
	RA_axis.track(-0.3)
	time.sleep(2)
	RA_axis.slew(1.4)
	time.sleep(4)
	RA_axis.slew(-1.3)
	time.sleep(3)
	RA_axis.slew(1.2)
	time.sleep(4)
	RA_axis.slew(.2)
	time.sleep(3)
	RA_axis.slew(-1.2)
	time.sleep(3)
	RA_axis.track(0.3)
	time.sleep(2)
	RA_axis.track(0.4)
	time.sleep(2)
	RA_axis.track(0.5)
	time.sleep(2)
	RA_axis.track(0.)
	time.sleep(2)
	'''


