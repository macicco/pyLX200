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
	def __init__(self,a,v):
		self.pointError=ephem.degrees('00:00:01')
		self.timestep=0.010
		self.acceleration=a
		self.a=a
		self.vmax=v
		self.beta=0
		self.v=0
		self.beta_target=0
		self.t2target=0
		self._vmax=0
		self.tracking=False
		self.vtracking=0
		self.end=False
		self.kill=False
		#self.say()

	def say(self):
		print self.acceleration,self.vmax,self.v
		print self.t_slope,self.beta_slope
		print self.beta,self.beta_target,self.t2target
		print 	self._vmax



	def slew(self,beta,blocking=False):
		self.tracking=False
		self.end=False
		self.beta_target=beta
		if not blocking:
			return
	        while not RA_axis.end:
			time.sleep(1)

	def track(self,v):
		self.tracking=True
		self.vtracking=v



	@threaded
	def run(self):
		while not self.kill:
			time.sleep(self.timestep)
			if self.tracking:
				self.tracktick()
			else:
				self.slewtick()
		return

	def tracktick(self):
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
		self.delta=self.beta_target-self.beta
		self.v=self.v+self.a*self.timestep

		sign=math.copysign(1,self.delta)
		self.beta_slope=(self.v*self.v)/(2*self.acceleration) 
		self.t_slope=self.v/self.acceleration  
		self.a=self.acceleration*sign

		#check if arrived to target
		if  abs(self.beta -self.beta_target) <= self.pointError:
			self.end=True
			self.v=0
			self.a=0

	   	#check if already at max speed
		if abs(self.v)>=abs(self.vmax):
			v_sign=math.copysign(1,self.v)
			if sign==v_sign:
				self.v=self.vmax*sign
				self.a=0
	
		#check if it is time to deccelerate
		if abs(self.delta) - self.beta_slope<=0:
			self.a=-self.acceleration*sign

		steps=self.v*self.timestep+self.a*(self.timestep*self.timestep)/2
		self.beta=self.beta+steps

		#print self.beta,self.v,self.a,steps

class mount:
	def __init__(self,a,v):
		self.axis1=axis(a,v)
		self.axis2=axis(a,v)
		self.run()


	def run(self):					
		self.axis1.run()
		self.axis2.run()

	def slew(self,x,y):
		self.axis1.slew(x)
		self.axis2.slew(y)

	def track(self,vx,vy):
		self.axis1.track(vx)
		self.axis2.track(vy)

	def compose(self,x,y):
		deltax=x-self.axis1.beta
		deltay=y-self.axis2.beta
		angle=math.atan2(y, x)
		print deltax,deltay,angle

	def coords(self):
		print self.axis1.beta,self.axis2.beta,self.axis1.v,self.axis2.v,self.axis1.a,self.axis2.a

	def end(self):
		self.axis1.kill=True
		self.axis2.kill=True


if __name__ == '__main__':
	#m=mount(1,1)
	a=ephem.degrees('01:00:00')
	v=ephem.degrees('05:00:00')
	m=mount(a,v)
	m.slew(0.5,0.5)
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


