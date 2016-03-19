#!/usr/bin/python

import math
import time,datetime
import threading
import ephem

def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class axis:
	def __init__(self,a,v,pointError):
		self.pointError=float(pointError)
		self.timesleep=0.0001
		self.timestepMax=0.5
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

	def say(self):
		print self.acceleration,self.vmax,self.v
		print self.t_slope,self.beta_slope
		print self.beta,self.beta_target,self.t2target
		print self._vmax



	def slew(self,beta,blocking=False):
		self.tracking=False
		print "TRACKING END"
		print "SLEW START"
		self.slewend=False
		self.beta_target=beta
		#self.v=self.vtracking
		if not blocking:
			return
	        while not self.slewend:
			time.sleep(1)

	def track(self,v):
		print "TRACKING START"
		self.tracking=True
		self.vtracking=v


	def sync(self,b):
		self.beta_target=b
		self.beta=b


	@threaded
	def run(self):
		self.T=time.time()
		while not self.kill:
			time.sleep(self.timesleep)
			now=time.time()
			delta=now-self.T
			#if delta<self.timestep/3:
			#	continue
			self.T=now
			self.timestep=delta
			#print delta

			if self.tracking:
				self.tracktick()
			else:
				self.slewtick()


	def tracktick(self):
		steps=self.vtracking*self.timestep
		self.beta=self.beta+steps

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

	def slewtick(self):
		if self.slewend:
			#This change to tracktick() in run()
			#print "Change_to_track"
			return
		self.delta=self.beta_target-self.beta
		self.v=self.v+self.a*self.timestep

		sign=math.copysign(1,self.delta)
		self.beta_slope=(self.v*self.v)/(2*self.acceleration) 
		self.t_slope=self.v/self.acceleration  
		self.a=self.acceleration*sign


	   	#check if already at max speed
		if abs(self.v)>=abs(self._vmax):
			v_sign=math.copysign(1,self.v)
			if sign==v_sign:
				self.v=self._vmax*sign
				self.a=0
	
		#check if it is time to deccelerate
		if abs(self.delta) - self.beta_slope<=0:
			self.a=-self.acceleration*sign

		#check if arrived to target	
		if  abs(self.delta) <= self.pointError:
			self.slewend=True
			print "SLEW END"
			self.v=self.vtracking
			self.a=0
			steps=self.delta
			self.beta=self.beta+steps
			self.track(self.vtracking)
			#self.beta=ephem.degrees(self.beta_target)
			return

		steps=self.v*self.timestep+self.a*(self.timestep*self.timestep)/2
		self.beta=self.beta+steps
		self.deltaOld=self.delta

		#print self.beta,self.v,self.a,steps

class mount:
	def __init__(self,a,v,pointError):
		self.axis1=axis(a,v,pointError)
		self.axis2=axis(a,v,pointError)
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
		deltax=x-self.axis1.beta
		deltay=y-self.axis2.beta
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
	DEC=ephem.degrees('15:00:00')
	m.slew(RA,DEC)
	t=0
	while t<15:
		t=t+m.axis1.timestep*2
		time.sleep(m.axis1.timestep*2)
		m.coords()
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


