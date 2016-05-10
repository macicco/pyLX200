#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import zmq
import time,datetime
import ephem
import json
import tle
import math

from config import *



class tracker:
	def __init__(self):
		self.last={}
		self.timestep=0.1
		context = zmq.Context()
		self.socketStream = context.socket(zmq.SUB)
		#CONFLATE: get only one message (do not work with the stock version of zmq, works from ver 4.1.4)
		self.socketStream.setsockopt(zmq.CONFLATE, 1)
		self.socketStream.connect ("tcp://localhost:%s" % zmqStreamPort)
		self.socketStream.setsockopt(zmq.SUBSCRIBE, 'values')
	
		self.socketCmd = context.socket(zmq.REQ)
		self.socketCmd.connect ("tcp://localhost:%s" % zmqCmdPort)

		self.observerInit()
		self.TLEs=tle.TLEhandler()
		self.a=0
		self.go2rise=False
		self.RUN=True

	def observerInit(self):
		self.socketCmd.send('@getObserver')
		reply=json.loads(self.socketCmd.recv())
		self.observer=ephem.Observer()
		self.observer.lat=reply['lat']
		self.observer.lon=reply['lon']
		self.observer.horizon=reply['horizon']
		self.observer.elev=reply['elev']
		self.observer.temp=reply['temp']
		self.observer.compute_pressure()

	def trackSatellite(self,sat):
		error=ephem.degrees('00:00:05')
		satRA,satDEC = self.go2sat(sat)
		vsatRA,vsatDEC = self.satSpeed(sat)
		self.sendTrackSpeed(vsatRA,vsatDEC)
		errorRA=ephem.degrees(abs(satRA-self.RA))
		errorDEC=ephem.degrees(abs(satDEC-self.DEC))
		if abs(errorRA)>=error or abs(errorDEC)>=error:
			print "Too much error. Slewing",(errorRA),(errorDEC),str(error)
			self.sendSlew(satRA,satDEC)
		else:
			pass
			print "OK",(errorRA),(errorDEC),str(error)

	def circle(self,re,dec,r,v):
		#not finished
		self.a=v*self.timestep+self.a
		vRA=r*math.sin(self.a)
		vDEC=r*math.cos(self.a)
		self.sendTrackSpeed(vRA,vDEC)


	def sendSlew(self,RA,DEC):
		self.socketCmd.send(':Sr '+str(RA))
		reply=self.socketCmd.recv()
		self.socketCmd.send(':Sd '+str(DEC))
		reply=self.socketCmd.recv()
		self.socketCmd.send(':MS')
		reply=self.socketCmd.recv()

	def sendTrackSpeed(self,vRA,vDEC):
		self.socketCmd.send('@setTrackSpeed '+str(vRA)+' '+str(vDEC))
		reply=self.socketCmd.recv()


	def run(self):
		while self.RUN:
			time.sleep(self.timestep)
			self.values=self.lastValue()
			#Call to the RA/DEC primitives for accuracy
			self.socketCmd.send('@getRA')
			self.RA=ephem.hours(self.socketCmd.recv())
			self.socketCmd.send('@getDEC')
			self.DEC=ephem.degrees(self.socketCmd.recv())
			#self.trackSatellite('METEOSAT-7')
			#self.trackSatellite('KAZSAT 3')
			self.trackSatellite('ISS')
			#self.trackSatellite('DEIMOS 2')	
			#self.circle(0,0,ephem.degrees('0:30:00'),0.1)

	def go2sat(self,sat):
			observer=self.observer
			s=self.TLEs.TLE(sat)
			observer.date=ephem.Date(datetime.datetime.utcnow())
			s.compute(observer)
			ra,dec=(s.ra,s.dec)
			if self.go2rise:
			    if s.alt<0:
				info=observer.next_pass(s)
				ra,dec=observer.radec_of(info[1],observer.horizon)
				
			return ra,dec


	def satSpeed(self,sat):
			seconds=self.timestep
			observer=self.observer
			s=self.TLEs.TLE(sat)
			observer.date=ephem.Date(datetime.datetime.utcnow())
			s.compute(observer)
			RA0=s.ra
			DEC0=s.dec
			observer.date=observer.date+ephem.second*seconds
			s.compute(observer)
			RA1=s.ra
			DEC1=s.dec
			vRA=ephem.degrees((RA1-RA0)/seconds-ephem.hours('00:00:01'))
			vDEC=ephem.degrees((DEC1-DEC0)/seconds)
			if self.go2rise:
			    if s.alt<0:
				vRA,vDEC=(0,0)
  			return (vRA,vDEC)

	def lastValue(self):
		self.last
		try:
			m= self.socketStream.recv(flags=zmq.NOBLOCK)
			topic, msg  = demogrify(m)
			self.last=msg
		except:
			msg=self.last
    		return msg

	def end(self):
		self.RUN=False

if __name__ == '__main__':
	t=tracker()
	t.run()
	try:
		t.run()
	except:
		t.end()

	

