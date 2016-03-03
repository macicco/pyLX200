#!/usr/bin/python

import math
import time,datetime
import threading


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class axis:
	def __init__(self,a,v):
		self.timestep=0.001
		self.pointError=0.001
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
		#print datetime.datetime.now()
		while not self.kill:
			time.sleep(self.timestep)
			if self.tracking:
				self.tracktick()
			else:
				self.slewtick()
		return

	def tracktick(self):

		sign=math.copysign(1,self.vtracking)
		self.beta_slope=(self.v*self.v)/(2*self.acceleration) 
		self.t_slope=self.v/self.acceleration  
		self.a=self.acceleration*sign
		self.v=self.v+self.a*self.timestep

	   	#check if already at max speed
		if abs(self.v)>=abs(self.vtracking):
			v_sign=math.copysign(1,self.v)
			if sign==v_sign:
				self.v=self.vtracking
				self.a=0

		steps=self.v*self.timestep+self.a*(self.timestep*self.timestep)/2
		self.beta=self.beta+steps
		print self.beta,self.v,self.a,steps*1000

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

		print self.beta,self.v,self.a,steps*1000

class mount:
	def __init__(self,a,v):
		RA_axis=axis(a,v)
		DEC_axis=axis(a,v)						

if __name__ == '__main__':
	RA_axis=axis(1.,1.)
	RA_axis.run()

	RA_axis.track(-0.3)
	time.sleep(2)

	'''
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
	'''

	RA_axis.track(0.3)
	time.sleep(2)
	RA_axis.track(0.4)
	time.sleep(2)
	RA_axis.track(0.5)
	time.sleep(2)

	RA_axis.kill=True
