#!/usr/bin/python

import math
import time,datetime
import threading
import ephem

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
		self.timestepMax=0.1
		self.timestepMin=0.000001
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
		#self.say()

	def setName(self,name):
		self.name=name
		if self.debug:
			self.logfile=open(str(self.name)+".log",'w')

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
			steps=0
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
				#print self.name,"MAX V:",self.v

		self.v=self.v+self.a*self.timestep
		steps=self.v*self.timestep+self.a*(self.timestep*self.timestep)/2
		self.beta=self.beta+steps
		self.deltaOld=self.delta

		#print self.beta,self.v,self.a,"STEPS:",steps
		
		return steps

	def doSteps(self,steps):
		#sleep
		time.sleep(self.timesleep)
		if self.debug:
			line=str(self.name)+" "+str(self.timesleep)+" "+str(steps)
			if steps>=self.timesleep:
				line=line+" NOT TIME!"
			self.logfile.write(line+'\n')
		pass

#Stepper implementation
class AxisDriver(axis):
	def __init__(self,a,v,pointError):
		super(AxisDriver, self).__init__(a,v,pointError)
		self.stepsPerRevolution=200*8
		self.corona=50
		self.plate=200
		self.FullTurnSteps=self.plate*self.stepsPerRevolution/self.corona
		self.stepsRest=0
		self.pulseWidth=0.001
		self.pointError=math.pi*2/self.FullTurnSteps
		self.timestepMin=2*self.pulseWidth
		print self.name,"Min step (point Error)",ephem.degrees(self.pointError)

	
	def doSteps(self,delta):

		steps=(self.FullTurnSteps*delta)/(math.pi*2)+self.stepsRest
		Isteps=round(steps)
		self.stepsRest=steps-Isteps
		if Isteps<0:
			dir=-1
		else:
			dir=1
		Isteps=int(abs(Isteps))
		if Isteps==0:
			pulseLasting=0
		else:
			pulseLasting=self.timesleep/Isteps

		#print self.timesleep,self.name,ephem.degrees(delta),dir,Isteps,self.stepsRest,pulseLasting
		if self.debug:
			line=str(self.name)+" timesleep "+str(self.timesleep)+" delta: "+str(delta)+" istep: "+str(Isteps)
			if delta>=self.timesleep:
				line=line+" NOT TIME!"
			self.logfile.write(line+'\n')
			#print line

		if Isteps==0:
			time.sleep(self.timesleep)
			return		

		if pulseLasting-self.pulseWidth <0:
			print self.name,"timestep: to low for pulsewidth"
			for p in range(Isteps):
				pin=1
				time.sleep(self.pulseWidth)
				pin=0
				time.sleep(self.pulseWidth*0.1)

		else:
			for p in range(Isteps):
				pin=1
				time.sleep(self.pulseWidth)
				pin=0
				time.sleep(pulseLasting-self.pulseWidth)




class mount:
	def __init__(self,a,v,pointError):
		self.axis1=AxisDriver(a,v,pointError)
		self.axis2=AxisDriver(a,v,pointError)
		#self.axis1=axis(a,v,pointError)
		#self.axis2=axis(a,v,pointError)
		self.axis1.setName("RA")
		self.axis2.setName("DEC")
		self.T0=time.time()
		self.run()


	def run(self):					
		self.axis1.run()
		self.axis2.run()

	def slew(self,x,y):
		self.setVmax(x,y)
		self.axis1.slew(x)
		self.axis2.slew(y)

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
	a=ephem.degrees('02:00:00')
	v=ephem.degrees('05:00:00')
	e=ephem.degrees('00:01:00')
	m=mount(a,v,e)
	m.trackSpeed(e,0)
	RA=ephem.hours('01:00:00')
	DEC=ephem.degrees('-15:00:00')
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


